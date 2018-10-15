"""
instancer.py

Author :    Alejandro Cabrera
            voidreamer@gmail.com
            linkedin.com/in/voidreamer
"""
from pymel.core import *
import maya.mel
import modelEd
import functools
import selectHeaviest
import re

__version__ = "0.1.0"

insLst = []
instances = []

lst = []
dic = {}


def closed_window(*args):
    try:
        iconTextButton("bip", e=True, bgc=[.361, .361, .361])
    except RuntimeError as rerr:
        print rerr


def list_instances(*args):
    sele = ls(dag=True)
    ins = []
    if textScrollList('cinst', ex=True, q=True):
        textScrollList('cinst', e=True, removeAll=True)
        for i in sele:
            if len(i.getInstances()) > 1:
                for j in i.getInstances():
                    if objectType(j) == 'mesh':
                        ins.append(j.getAllParents()[0])
        textScrollList('cinst', e=True, append=ins)


def renamer(obj, remove=True):
    return re.sub('_INS[0-9]', '', str(obj))


def start():
    global lst
    global dic

    lst = selectHeaviest.get_lists('lst')
    dic = selectHeaviest.get_lists('dic')

    t = textScrollList('list', e=True)
    try:
        iconTextButton("bip", e=True, bgc=[1, 0.49, 0.245])
        template = uiTemplate('temp', force=True)
        if window('instanceWindow', q=True, ex=True):
            return
    except RuntimeError as runErr:
        print "runErr: ", runErr

    def item_selected(*args):
        if button('instance_btn', q=True, ex=True):
            button('instance_btn', e=True, enable=True)
        t.removeAll()
        io = []  # prospects or instanced objects
        ind = args[0].getSelectIndexedItem()[0] - 1

        for i in lst:
            if dic.get(i.getChildren()[0]) == insLst[ind]:  # selected index value = lst value
                io.append(i)

        t.append(io)
        t.selectAll()
        select(io)

        if window('medwin1', q=True, ex=True):
            modelEd.update_objects(io)
            if objExists("mvcam*Shape*"):
                modelEd.viewFit("mvcam*Shape*")

    def del_instance(*args):
        sele = ls(textScrollList('cinst', q=True, ai=True))
        for i in sele:
            a = duplicate(i, rc=True)
            rename(a, renamer(a[0], True))
            delete(i)
        global dic, lst
        dic, lst = selectHeaviest.update_lists(sele, True)
        list_instances()

    def instance_selected(*args):
        if button('instance_btn', q=True, ex=True):
            button('instance_btn', e=True, enable=False)
        objs = ls(sl=True)
        obmesh = []
        if objs:
            geo = objs[0]
            for o in objs:
                if objectType(o.getChildren()[0]) == 'mesh':
                    xform(o, centerPivots=True, ztp=True)
                    ins = instance(geo, n=o + '_INS')
                    instances.append(ins)  # store to a list
                    bbx = xform(o, q=True, bb=True, ws=True)  # calculate center
                    centerX = (bbx[0] + bbx[3]) / 2.0
                    centerY = (bbx[1] + bbx[4]) / 2.0
                    centerZ = (bbx[2] + bbx[5]) / 2.0
                    move(centerX, centerY, centerZ, ins, rpr=True)
                    obmesh.append(o)

            ind = textScrollList('tinst', q=True, sii=True)[0]
            textScrollList('tinst', e=True, rii=ind)

            global lst, dic, insLst
            insLst.pop(ind - 1)
            delete(obmesh)
            dic, lst = selectHeaviest.update_lists(obmesh, True)
            list_instances()
        else:
            return

    def get_instances(*args):
        gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')
        progressBar(gMainProgressBar,
                    edit=True,
                    beginProgress=True,
                    isInterruptable=True,
                    status='Getting prospects ...',
                    maxValue=len(lst))
        global insLst
        insLst = []
        if textScrollList('tinst', q=True, ex=True):
            textScrollList('tinst', e=True, removeAll=True)

        for i in range(0, len(lst)):
            if dic.get(lst[i].getChildren()[0]) not in insLst:  # Checks for same number of triangles groups
                if dic.values().count(dic.get(lst[i].getChildren()[0])) > 1:  # same num of tris in more than 1 objs
                    insLst.append(dic.get(lst[i].getChildren()[0]))

            if progressBar(gMainProgressBar, query=True, isCancelled=True):
                break
            progressBar(gMainProgressBar, edit=True, step=1)
        progressBar(gMainProgressBar, edit=True, endProgress=True)

        if insLst:
            for i in insLst:  # format the list
                ts = textScrollList('tinst', e=True, append='Prospects {} - {} tris/obj'.format(insLst.index(i) + 1, i))
            ts.selectCommand(functools.partial(item_selected, ts))
        else:
            ts = textScrollList('tinst', e=True, append='No prospects for instancing found')

    with window('instanceWindow', menuBar=True, menuBarVisible=True, title="Instancer", cc=closed_window,
                rc=lambda *args: inViewMessage(amg='show', pos='midCenter', fade=True, bkc=0xAACCFF22)) as winIns:
        with template:
            with frameLayout(collapsable=False, w=150, label="Current instances"):
                textScrollList('cinst', h=100, w=150)
                list_instances()
                rainstBtn = button(label='Rem all', h=20)

            with frameLayout(collapsable=True, collapse=True, label='Create Instances'):

                text("Instance prospects list", font="tinyBoldLabelFont")
                textScrollList('tinst', h=100, w=150)
                button(label='Check for prospects\nin the scene', command=get_instances, w=50, h=40)

                insBtn = button('instance_btn', label='Instance!', bgc=[0.576, 0.784, 0.939], enable=False)
                with horizontalLayout():
                    button(label="invert X", c=lambda *args: setAttr(ls(sl=True)[0]+'.scaleX', (getAttr(ls(sl=True)[0]+'.scaleX') * -1)))
                    button(label="invert Y", c=lambda *args: setAttr(ls(sl=True)[0]+'.scaleY', (getAttr(ls(sl=True)[0]+'.scaleY') * -1)))
                    button(label="invert Z", c=lambda *args: setAttr(ls(sl=True)[0]+'.scaleZ', (getAttr(ls(sl=True)[0]+'.scaleZ') * -1)))


    insBtn.setCommand(instance_selected)
    rainstBtn.setCommand(del_instance)
