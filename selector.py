"""
selectHeaviest.py

Author :    Alejandro Cabrera
            voidreamer@gmail.com
            linkedin.com/in/voidreamer
"""

from pymel.core import *
import modelEd
import instancer
import functools
import maya.mel

__version__ = "0.1.0"

dic = {}
lst = []


def get_lists(obj):
    if obj == 'lst':
        return lst
    elif obj == 'dic':
        return dic


def update_lists(obj=[], remove=False):
    global dic
    global lst

    dic = {}
    lst = []

    allGeo = ls(dag=True, type='mesh', fl=True)
    parents = []

    if allGeo:
        gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')
        progressBar(gMainProgressBar,
                    edit=True,
                    beginProgress=True,
                    isInterruptable=True,
                    status='Evaluating objects ...',
                    maxValue=len(allGeo))

        for geo in allGeo:
            if progressBar(gMainProgressBar, query=True, isCancelled=True):
                break
            progressBar(gMainProgressBar, edit=True, step=1)
            if geo.getParent() not in parents:
                parents.append(geo.getParent())  # validates to not get duplicated shapes
                ntriangles = polyEvaluate('%s' % geo, t=True)  # counts the number of triangles
                dic.update({geo: ntriangles})

        progressBar(gMainProgressBar, edit=True, endProgress=True)

    else:

        template = uiTemplate('temp', force=True)
        template.define(frameLayout, borderVisible=True, labelVisible=False)

        with window(menuBar=True, menuBarVisible=True, title="Heavy topology diagnostic v0.1") as tempwin:
            with template:
                with columnLayout(rowSpacing=5):
                    text('Sorry, there are no polygonal objects in the scene', font='boldLabelFont')
                    button(label='OK', c=lambda *args: deleteUI(tempwin))
                    return

    for key, value in sorted(dic.iteritems(), key=lambda (k, v): (v, k)):
        lst.append(key.getParent())

    if remove:
        return dic, lst


def init():
    global dic
    global lst

    update_lists()

    try:
        stt = sum(dic.values())  # stt stands for sum total triangles
        avg = sum(dic.values()) / len(dic)
        maxtri = max(dic.values())
    except ZeroDivisionError:
        return

    def fl_expand(*args):

        if 'ntris' in args:
            frameLayout('nobj', e=True, collapse=True)
            frameLayout('nperc', e=True, collapse=True)

        elif 'nobj' in args:
            frameLayout('ntris', e=True, collapse=True)
            frameLayout('nperc', e=True, collapse=True)

        elif 'nperc' in args:
            frameLayout('ntris', e=True, collapse=True)
            frameLayout('nobj', e=True, collapse=True)

    def fl_collapse(*args):
        intSliderGrp(args[0] + '_slider', e=True, value=0)
        print "coll"

    def highlight_buttons(string):
        '''

        :param string: button name to highlight

        '''
        if string is not 'ball' and string is not 'bnone' and string is not 'item':
            button("bhv", edit=1, bgc=[.361, .361, .361])
            button("bcst", edit=1, bgc=[.361, .361, .361])
            button("bavg", edit=1, bgc=[.361, .361, .361])
            button("bnone", edit=1, bgc=[.361, .361, .361])
            button("ball", edit=1, bgc=[.361, .361, .361])
        else:
            button("bnone", edit=1, bgc=[.361, .361, .361])
            button("ball", edit=1, bgc=[.361, .361, .361])

        if string is not 'bnone':
            # button("bes", edit=1, enable=True)
            # button("brs", edit=1, enable=True)
            iconTextButton("bmv", edit=1, enable=True)
            button("ball", edit=1, bgc=[0.576, 0.784, 0.939])
        else:
            # button("brs", edit=1, enable=False)
            iconTextButton("bmv", edit=1, enable=False)
            # button("bes", edit=1, enable=False)

        if string is not 'item':
            button(string, edit=1, bgc=[0.576, 0.784, 0.939])
        else:
            button("ball", edit=1, bgc=[.361, .361, .361])

    def custom():
        template = uiTemplate('temp', force=True)
        try:
            if window('customWindow', q=True, ex=True):
                return
        except RuntimeError as runErr:
            print "runErr: ", runErr

        with window('customWindow', menuBar=True, menuBarVisible=True, title="Custom object selection") as win:
            # start the template block
            with template:
                with columnLayout(rowSpacing=5):
                    with frameLayout('nobj', label='By Number of objects', collapsable=True,
                                     ec=functools.partial(fl_expand, 'nobj'),
                                     cc=functools.partial(fl_collapse, 'nobj')):
                        text("From heaviest to lightest", font="tinyBoldLabelFont")
                        with columnLayout(adjustableColumn=True):
                            intSliderGrp("nobj_slider", field=True, minValue=1,
                                         maxValue=len(lst), value=1, enable=True)

                    with frameLayout('ntris', label='By Max triangles', collapsable=True,
                                     collapse=True, ec=functools.partial(fl_expand, 'ntris'),
                                     cc=functools.partial(fl_collapse, 'ntris')):
                        with columnLayout(adjustableColumn=True):
                            intSliderGrp("ntris_slider", field=True, minValue=dic.get(lst[0].getChildren()[0]),
                                         maxValue=maxtri, value=dic.get(lst[0].getChildren()[0]), enable=True)

                    with frameLayout('nperc', label='By percentage', collapsable=True, collapse=True,
                                     ec=functools.partial(fl_expand, 'nperc'),
                                     cc=functools.partial(fl_collapse, 'nperc')):

                        with columnLayout(adjustableColumn=True):
                            intSliderGrp("nperc_slider", field=True, minValue=(100 / len(lst)) + 1,
                                         maxValue=100, value=(100 / len(lst)) + 1, enable=True)

                    def update_custom(lista):
                        t = textScrollList('list', e=True)
                        t.removeAll()
                        t.append(lista)
                        textScrollList('list', e=True, selectIndexedItem=1)

                        item = t.getSelectItem()[0].split("=")[0]
                        select(item)
                        ls(item)

                    def update_list(*args):
                        lista = []
                        if not frameLayout('nobj', query=True, collapse=True):
                            for i in range(1, intSliderGrp("nobj_slider", q=True, value=True) + 1):
                                try:
                                    lista.append("%s =  %s triangles" % (lst[i * -1], dic.get(lst[i * -1].getChildren()[0])))
                                except IndexError as inde:
                                    print "index exceeded"

                        elif not frameLayout('ntris', query=True, collapse=True):
                            for i in lst:
                                if dic.get(i.getChildren()[0]) <= intSliderGrp("ntris_slider", q=True, value=True):
                                    lista.append("%s =  %s triangles" % (i, dic.get(i.getChildren()[0])))
                            # to do :
                        elif not frameLayout('nperc', query=True, collapse=True):
                            for i in range(1, (len(lst) * intSliderGrp("nperc_slider", q=True, value=True) / 100) + 1):
                                lista.append("%s =  %s triangles" % (lst[i * -1], dic.get(lst[i * -1].getChildren()[0])))
                            # to do :
                        update_custom(lista)
                        deleteUI(win, window=True)

                    bcustom = button("bcustom", label='Update list', bgc=[0.576, 0.784, 0.939])
                    bcustom.setCommand(update_list)

    def export_selected(*args):
        print args
        if args[0] == 'FBX':
            loadPlugin("fbxmaya")  # LOAD PLUGIN
            location = fileDialog2(ds=2, fileFilter="FBX files (*.fbx)")  # Dialog to save the FBX file
            if location:
                print "valid location"
                mel.FBXImportMode(v="Add")
                return mel.FBXImport(f=location[0], t="TAKE")
        elif args[0] == 'MAYA':
            location = fileDialog2(ds=2, fileFilter="Maya files (*.ma)")
            if location:
                print "valid location"
                mel.file(rename=location[0])
                mel.file(es=True, type="mayaAscii")
                return location[0]

    def reducer():
        def red(*args):
            obj = ls(sl=True)
            if objectType(obj[0].getChildren()[0]) == 'mesh':
                if len(obj) == 1:
                    polyReduce(obj[0], ver=1, p=val.getValue())
                else:
                    for i in obj:
                        polyReduce(i, ver=1, p=val.getValue())

        template = uiTemplate('temp', force=True)
        try:
            iconTextButton("brd", e=True, bgc=[1, 0.49, 0.245])
            if window('reducerWindow', q=True, ex=True):
                return

            with window('reducerWindow', menuBar=True, menuBarVisible=True, title="Reducer",
                        cc=lambda *args: iconTextButton("brd", e=True, bgc=[.361, .361, .361])) as redWin:
                with template:
                    with frameLayout(label="Percentage"):
                        val = intSliderGrp("reduc_slider", field=True, minValue=1,
                                           maxValue=100, value=50, enable=True)
                        button(label="Reduce", c=red)

        except RuntimeError as runErr:
            print "runErr: ", runErr

    def proxyfier():
        obj = ls(sl=True)
        template = uiTemplate('temp', force=True)

        try:
            iconTextButton("bpp", e=True, bgc=[1, 0.49, 0.245])
            if window('proxyWindow', q=True, ex=True):
                return

            def get_num():
                num = 1
                ok = 1
                while ok:
                    ok = namespaceInfo(listNamespace=True).count("model_low" + str(num))
                    if ok:
                        num += 1
                    return num

            def proxy_selected(*args):
                item = args[0].getSelectItem()[0]
                button("blowproxy", e=True, enable=True)
                button("bhighproxy", e=True, enable=True)

            def proxy_switch(*args):
                print args
                try:
                    tproxy = textScrollList('cproxy', q=True, selectItem=True)[0]
                except RuntimeError:
                    print ""

                if tproxy:
                    if args[0] == 'low':
                        mel.proxySwitch(tproxy)
                        print tproxy
                    elif args[0] == 'high':
                        print tproxy.replace("RN","_highRN")
                        mel.proxySwitch(tproxy.replace("RN", "_highRN"))

            def update_proxy_lst():
                try:
                    refs = []  # Lists references in scene
                    for r in ls(type='reference'):
                        if r.find("_high") is -1 and r != 'sharedReferenceNode':  # avoid selecting the high
                            if referenceQuery(r, rfn=True):
                                print r
                                refs.append(r)
                    print refs
                    if textScrollList('cproxy', q=True, ex=True):
                        textScrollList('cproxy', e=True, removeAll=True, append=refs)
                except RuntimeError as re:
                    print re

            def loadpfile(*args):

                if args[0] == 'low':
                    ubilow = fileDialog2(ds=2, fileFilter="Maya files (*.ma)")
                    if ubilow:
                        if textFieldButtonGrp('proxy_low', q=True, ex=True):
                            textFieldButtonGrp('proxy_low', e=True, text=ubilow[0])
                    else:
                        return
                elif args[0] == 'high':
                    ubihigh = fileDialog2(ds=2, fileFilter="Maya files (*.ma)")
                    if ubihigh:
                        if textFieldButtonGrp('proxy_high', q=True, ex=True):
                            textFieldButtonGrp('proxy_high', e=True, text=ubihigh[0])
                    else:
                        return

            def load_proxy(*args):
                num = get_num()

                ubilow = ""
                ubihigh = ""
                try:
                    if textFieldButtonGrp('proxy_low', q=True, ex=True):
                        ubilow = textFieldButtonGrp('proxy_low', q=True, text=True)

                    if textFieldButtonGrp('proxy_low', q=True, ex=True):
                        ubihigh = textFieldButtonGrp('proxy_high', q=True, text=True)

                    if ubilow and ubihigh:

                        ok = mel.file(ubilow, r=True, type="mayaAscii", namespace="model_low" + str(num))
                        if ok:
                            mel.setAttr("model_low" + str(num) + "RN.proxyTag", "low", type="string")
                            mel.proxyAdd("model_low" +str(num) + "RN", ubihigh, "_high")
                        if textFieldButtonGrp('proxy_low', q=True, ex=True):
                            textFieldButtonGrp('proxy_low', e=True, text=ubilow)

                        if textFieldButtonGrp('proxy_high', q=True, ex=True):
                            textFieldButtonGrp('proxy_high', e=True, text=ubihigh)

                        update_proxy_lst()

                    else:
                        print "nope disk"
                except RuntimeError as rerr:
                    print rerr

            with window('proxyWindow', menuBar=True, menuBarVisible=True, title="Proxyfier",
                        cc=lambda *args: iconTextButton("bpp", e=True, bgc=[.361, .361, .361]), w=100) as proxyWin:
                with template:
                    with frameLayout(collapsable=False, label="Current proxies"):
                        tproxy = textScrollList('cproxy', w=100)
                    with frameLayout(label=""):
                        bes = button("bes", label='Export selected to disk', c=functools.partial(export_selected,'MAYA'))
                        textFieldButtonGrp('proxy_low', label='Low', buttonLabel='<<',
                                           bc=functools.partial(loadpfile, 'low'))
                        textFieldButtonGrp('proxy_high', label='High', buttonLabel='<<',
                                           bc=functools.partial(loadpfile, 'high'))
                        button(label="Proxify!", bgc=[0.576, 0.784, 0.939], c=lambda *args: load_proxy())
                        button("blowproxy", label="Switch to low", c=functools.partial(proxy_switch, 'low'), enable=False)
                        button("bhighproxy", label="Switch to high", c=functools.partial(proxy_switch, 'high'), enable=False)

                        update_proxy_lst()
            tproxy.selectCommand(functools.partial(proxy_selected, tproxy))

        except RuntimeError as runErr:
            print "runErr: ", runErr

    def create_win():
        template = uiTemplate('temp', force=True)
        template.define(frameLayout, borderVisible=True, labelVisible=False)

        try:
            if window('mainwin1', q=True, ex=True):
                return
        except RuntimeError as runErr:
            print "runErr: ", runErr

        def override_visual(*args):
            obj = ls(sl=True)
            if len(obj) == 1:
                if obj:
                    setAttr('%s.overrideEnabled' % obj[0], args[0])
                    setAttr('%s.overrideLevelOfDetail' % obj[0], args[0])
            else:
                for i in obj:
                    if i:
                        setAttr('%s.overrideEnabled' % i, args[0])
                        setAttr('%s.overrideLevelOfDetail' % i, args[0])

        with window('mainwin1', menuBar=True, menuBarVisible=True, title="Heavy topology diagnostic v0.1-alpha") as win:
            with template:
                # with columnLayout(rowSpacing=5):
                with frameLayout():
                    # with columnLayout():
                    with horizontalLayout():
                        text('Number of polygon objects in scene\t\t', al="left", font="obliqueLabelFont")
                        textField(text=len(lst), editable=False, w=10, bgc=[0.361, 0.361, 0.461])
                    with horizontalLayout():
                        text('Number of triangles in scene\t\t', al="left", font="obliqueLabelFont")
                        textField(text=stt, editable=False, w=10, bgc=[0.361, 0.361, 0.461])
                    with horizontalLayout():
                        text('Average triangles per object in scene\t', al="left", font="obliqueLabelFont")
                        textField(text=avg, editable=False, w=5, bgc=[0.361, 0.361, 0.461])
                    text('Show objects by:', font="tinyBoldLabelFont")
                    with horizontalLayout():
                        bhv = button("bhv", label='Heaviest', bgc=[0.576, 0.784, 0.939])
                        bavg = button("bavg", label='Heavier than avg')
                        bcst = button("bcst", label='Custom')
                    with horizontalLayout():
                        with paneLayout(configuration="horizontal2"):

                            fapnd = []
                            for i in lst:  # lst has the items sorted by triangles
                                if dic.get(i.getChildren()[0]) >= dic.get(
                                        lst[-1].getChildren()[0]):  # dic has both values and shapes
                                    fapnd.append("%s =  %s triangles" % (i, dic.get(i.getChildren()[0])))
                                    select(i)

                            t = textScrollList('list', h=200, w=200, numberOfRows=len(lst), append=fapnd,
                                               allowMultiSelection=True,
                                               showIndexedItem=4, selectIndexedItem=1, bgc=[0.176, 0.284, 0.339])
                            with horizontalLayout():
                                ball = button("ball", label='all', bgc=[0.576, 0.784, 0.939])
                                bnone = button("bnone", label='none')

                        with paneLayout(configuration='horizontal3'):
                            with paneLayout(configuration='quad', separatorThickness=1):
                                with frameLayout():
                                    bip = iconTextButton("bip", st='iconAndTextHorizontal', i1='ghost.png',
                                                         l='Instancer')

                                with frameLayout():
                                    bpp = iconTextButton('bpp', st='iconAndTextHorizontal',
                                                         i1='polyMirrorGeometry.png', l='Proxyfier', h=60)

                                with frameLayout():
                                    brd = iconTextButton('brd', st='iconAndTextHorizontal', i1='polyReduce.png',
                                                         l='Reducer')

                                with frameLayout():
                                    with horizontalLayout():
                                        iconTextButton(st='iconOnly', i1='lattice.xpm',
                                                                ann='Make bounding box',
                                                                c=functools.partial(override_visual, 1))
                                        iconTextButton(st='iconOnly', i1='cube.xpm', ann='Make normal',
                                                               c=functools.partial(override_visual, 0))
                                    button(label='Display type')

                            with frameLayout():
                                bmv = iconTextButton("bmv", st='iconOnly', i1='interactivePlayback.png',
                                                     l='Load model viewer', h=60, ann='Model Viewer')

        def item_selected(*args):
            item = t.getSelectItem()[0].split("=")[0]

            print "item", item
            select(item)
            highlight_buttons('item')

            if window('medwin1', q=True, ex=True):
                modelEd.update_objects(ls(item))  # needs the 'ls' to actually select the object in scene
                if objExists("mvcam*Shape*"):
                    modelEd.viewFit("mvcam*Shape*")

        def bavg_pressed(*args):
            highlight_buttons('bavg')

            t.removeAll()
            ho = []

            for i in lst:  # lst has the items sorted by triangles
                if dic.get(i.getChildren()[0]) >= avg:  # dic has both values and shapes
                    ho.append(i)
                    t.append("%s =  %s triangles" % (i, dic.get(i.getChildren()[0])))

            t.selectAll()
            select(ho)

            if window('medwin1', q=True, ex=True):
                modelEd.update_objects(ho)
                if objExists("mvcam*Shape*"):
                    modelEd.viewFit("mvcam*Shape*")

        def bhv_pressed(*args):
            t.removeAll()
            hvo = []  # List, because there can be more than one heaviest object (draw)

            for i in dic:
                if dic.get(i) == dic.get(lst[-1].getChildren()[0]):
                    hvo.append(i.getParent())
                    t.append("%s =  %s triangles" % (i.getParent(), dic.get(i)))

            t.selectAll()
            if window('medwin1', q=True, ex=True):
                modelEd.update_objects(hvo)
                if objExists("mvcam*Shape*"):
                    modelEd.viewFit("mvcam*Shape*")

            select(hvo)
            highlight_buttons('bhv')

        def ball_pressed(*args):
            t.selectAll()
            sa = []
            for se in t.getAllItems():
                select(se.split("=")[0], add=True)
                sa.append(se.split("=")[0])

            if window('medwin1', q=True, ex=True):
                modelEd.update_objects(ls(sa))
                if objExists("mvcam*Shape*"):
                    modelEd.viewFit("mvcam*Shape*")

            highlight_buttons('ball')

        def bnone_pressed(*args):
            t.deselectAll()
            select(clear=True)
            highlight_buttons('bnone')

        def bcst_pressed(*args):
            highlight_buttons('bcst')
            # print "DIR list ", dir(t)
            custom()

        def bmv_pressed(*args):
            # reload(modelEd)
            modelEd.start(1, ls(sl=True))
            modelEd.update_objects(ls(sl=True))

        def proxy_pressed(*args):
            proxyfier()

        def reducer_pressed(*args):
            reducer()

        def instancer_pressed(*args):
            instancer.start()


        bhv.setCommand(bhv_pressed)
        bavg.setCommand(bavg_pressed)
        bcst.setCommand(bcst_pressed)

        bnone.setCommand(bnone_pressed)
        ball.setCommand(ball_pressed)

        bmv.setCommand(bmv_pressed)
        # bes.setCommand(export_fbx)
        bip.setCommand(instancer_pressed)

        brd.setCommand(reducer_pressed)
        bpp.setCommand(proxy_pressed)

        # brs.setCommand(replace_selected)
        t.selectCommand(item_selected)

    create_win()
