# -*- coding: utf-8 -*-
"""
modelEd.py

Author :    Alejandro Cabrera
            voidreamer@gmail.com
            linkedin.com/in/voidreamer
"""
from pymel.core import *
import functools

ed = modelEditor()
win = []
sel = []  # global variable for current selected item in list
hiddenLayers = []
hiddenParents = []
vis_status = {'visible': True, 'hidden_parent': False, 'hidden_layer': False}

__version__ = "0.1.0"


def window_closed(*args):
    try:
        iconTextButton("bmv", e=True, bgc=[.361, .361, .361])
        if objExists("mvcam*"):
            delete("mvcam*")

        if objExists("med%s" % id):
            delete("med%s" % id)
            print ("med%s deleted" % id)
    except RuntimeError as rerr:
        print rerr

def update_form(vis_status):
    try:
        textFieldButtonGrp('tf_visible', e=True, visible=False)
        textFieldButtonGrp('tf_hid', e=True, visible=False)
        textFieldButtonGrp('tf_lhid', e=True, visible=False)
        textFieldButtonGrp('tf_phid', e=True, visible=False)
        textScrollList('tf_lhid_list', e=True, visible=False)
        textScrollList('tf_phid_list', e=True, visible=False)

        if vis_status:
            if vis_status.get('visible'):
                textFieldButtonGrp('tf_visible', e=True, visible=True)
            else:
                textFieldButtonGrp('tf_hid', e=True, visible=True)

            if vis_status.get('hidden_layer'):
                textFieldButtonGrp('tf_lhid', e=True, visible=True)
                textScrollList('tf_lhid_list', e=True, visible=True)

            if vis_status.get('hidden_parent'):
                textFieldButtonGrp('tf_phid', e=True, visible=True)
                textScrollList('tf_phid_list', e=True, visible=True)

    except RuntimeError as runterror:
        print runterror


def btn_flame(*args):
    global vis_status
    if sel[0]:
        if 'tf_hid' in args:
            setAttr('%s.visibility' % sel[0], 1)
            vis_status['visible'] = True

        elif 'tf_phid' in args:
            if hiddenParents:
                for i in hiddenParents:
                    setAttr('%s.visibility' % i, 1)
            vis_status['hidden_parent'] = False

        elif 'tf_lhid' in args:
            if hiddenLayers:
                for i in hiddenLayers:
                    setAttr('%s.visibility' % i, 1)
            vis_status['hidden_layer'] = False
        viewFit("mvcam*Shape*")
    update_form(vis_status)


def update_objects(obj):
    global sel
    global vis_status
    sel = obj

    if len(obj) is 1:
        if getAttr('%s.visibility' % obj[0]):  # if object is visible
            vis_status['visible'] = True
        else:
            vis_status['visible'] = False

        global hiddenLayers
        global hiddenParents

        hiddenLayers = []
        hiddenParents = []
        lay = ls(type="displayLayer")

        for par in obj[0].getAllParents():
            if not getAttr('%s.visibility' % par, 0):  # if parent is not visible
                hiddenParents.append(par)
                # if unhide:
                #    setAttr('%s.visibility' % par, 1)
                if any(elem in lay for elem in listConnections(par)):
                    for elem in listConnections(par):
                        if elem in lay:
                            hiddenLayers.append(elem)

        for i in listConnections(obj):
            if objectType(i) == 'displayLayer':
                if not getAttr('%s.visibility' % i):  # if object is in a hidden layer
                    hiddenLayers.append(i)

        if hiddenParents:
            vis_status['hidden_parent'] = True
            if textScrollList('tf_phid_list', q=True, ex=True):  # Hidden parent analysis
                textScrollList('tf_phid_list', e=True, removeAll=True)
                textScrollList('tf_phid_list', e=True, numberOfRows=len(hiddenParents), append=hiddenParents)
        else:
            vis_status['hidden_parent'] = False

        if hiddenLayers:
            vis_status['hidden_layer'] = True
            if textScrollList('tf_lhid_list', q=True, ex=True):  # Hidden layer analysis
                textScrollList('tf_lhid_list', e=True, removeAll=True)
                textScrollList('tf_lhid_list', e=True, visible=True, append=hiddenLayers)
        else:
            vis_status['hidden_layer'] = False

        update_form(vis_status)

    else:
        update_form({})

    if modelEditor(ed, q=True, ex=True) and ls("med1View*"):  # if viewer exists and set exists
        cobj = sets(ls("med1View*")[0], q=True, no=True)  # Current objects in set
        sets(ls("med1View*")[0], rm=cobj)  # Removes everything visible in the set
        sets(ls("med1View*")[0], add=obj)  # Adds everything from the argument


def start(idv, selinit):  # id of the model viewer and selected geo
    #    Create a window with a model editor and some buttons that
    #    change the editor's display of objects in the scene.
    #
    try:
        iconTextButton("bmv", e=True, bgc=[0.576, 0.784, 0.939])

        if window('medwin%s' % idv, q=True, ex=True):  # if this window actually exists, don't do  anything
            return
        win = window('medwin%s' % idv, title='Model viewer', widthHeight=[400, 400], cc=window_closed)
        form = formLayout()

        ed = modelEditor("med%s" % idv, displayAppearance='smoothShaded', udm=True, viewSelected=True,
                         hud=False, wbs=True, gr=False)

        column = columnLayout('true')

        #    Functions for editor buttons
        #

        def wire_selected(*args):
            modelEditor(ed, edit=True, displayAppearance='wireframe')

        def bb_selected(*args):
            modelEditor(ed, edit=True, displayAppearance='boundingBox')

        def smooth_selected(*args):
            modelEditor(ed, edit=True, displayAppearance='smoothShaded')

        #    Create some buttons that will alter the display appearance of
        #    objects in the model editor, eg. wireframe vs. shaded mode.
        #

        iconTextRadioCollection()
        iconTextRadioButton(st='iconAndTextHorizontal', i1='lattice.xpm', l='Wireframe', cc=wire_selected)
        iconTextRadioButton(st='iconAndTextHorizontal', i1='cube.xpm', l='Bounding Box', cc=bb_selected)
        iconTextRadioButton(st='iconAndTextHorizontal', i1='render_blinn.xpm', l='Smooth Shaded', cc=smooth_selected)

        separator(height=10, style='in')

        with frameLayout(label="Visibility", collapsable=True):
            with columnLayout():
                with horizontalLayout():
                    textFieldButtonGrp('tf_visible', text='Visible', buttonLabel=u"✅", editable=False,
                                       bgc=[0.361, 0.461, 0.361], cw=(1, 100), eb=False, visible=False)
                with horizontalLayout():
                    textFieldButtonGrp('tf_hid', text='Hidden', buttonLabel=u"🔥",
                                       bc=functools.partial(btn_flame, 'tf_hid'), editable=False,
                                       bgc=[0.361, 0.361, 0.461], cw=(1, 100), visible=False)
                with horizontalLayout():
                    textFieldButtonGrp('tf_temp', text='Template', buttonLabel=u"🔥",
                                       bc=functools.partial(btn_flame, 'tf_temp'), editable=False,
                                       bgc=[0.461, 0.361, 0.361], cw=(1, 100), visible=False)
                with columnLayout():
                    textFieldButtonGrp('tf_phid', text='Hidden by parent', buttonLabel=u"🔥",
                                       bc=functools.partial(btn_flame, 'tf_phid'), editable=False,
                                       bgc=[0.461, 0.461, 0.461], cw=(1, 100), visible=False)
                    textScrollList('tf_phid_list', visible=False, w=135, h=100)
                with columnLayout():
                    textFieldButtonGrp('tf_lhid', text='Hidden by layer:', buttonLabel=u"🔥",
                                       bc=functools.partial(btn_flame, 'tf_lhid'), editable=False,
                                       bgc=[0.361, 0.461, 0.461], cw=(1, 100), visible=False)
                    textScrollList('tf_lhid_list', visible=False, w=135, h=100)

                formLayout(form, edit=True,
                           attachForm=[(column, 'top', 0), (column, 'left', 0), (ed, 'top', 0), (ed, 'bottom', 0),
                                       (ed, 'right', 0)], attachNone=[(column, 'bottom'), (column, 'right')],
                           attachControl=(ed, 'left', 0, column))

        #    Create a camera for the editor.  This particular camera will
        #
        cam = ls("mvcam%s" % idv)

        if objExists("mvcam%s" % idv):
            camera(cam, e=True, ff='overscan')
        else:
            cam = camera(name="mvcam%s" % idv, centerOfInterest=5,
                         position=(0, 0, 0),
                         rotation=(-27.612504, 45, 0),
                         worldUp=(-0.1290301, 0.3488592, -0.1290301))
            select(selinit)
            viewFit("mvcam*Shape*")

        if idv is 2:
            connectAttr("mvcam1.translate", "mvcam2.translate")
            connectAttr("mvcam1.rotate", "mvcam2.rotate")
            connectAttr("mvcam1.scale", "mvcam2.scale")

        #    Attach the camera to the model editor.
        #
        modelEditor(ed, edit=True, camera=cam[0])

        showWindow(win)

    except RuntimeError as runErr:
        print "Sorry, please deselect objects and try again", runErr
