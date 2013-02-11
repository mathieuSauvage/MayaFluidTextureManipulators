'''
================================================================================
* VERSION 1.0
================================================================================
* AUTHOR:
Mathieu Sauvage mathieu@hiddenforest.fr
================================================================================
* INTERNET SOURCE:
https://github.com/mathieuSauvage/MayaFluidTextureManipulators.git
================================================================================
* MAIN FUNCTION:
FTM_addFluidTextureManipulators( fluid )
================================================================================
* DESCRIPTION:
This is a Maya python script that generate a rig of controllers to manipulate
the texture parameters of a fluid (origin, scale, rotate, implode position).
Please see the full description at the INTERNET SOURCE.
================================================================================
* USAGE:
- select a fluid then copy/paste this into a Maya python script editor and
execute it.
- put the script into a python script folder that Maya know, then use an import
command to use the script and call the main function with appropriate parameters.  
================================================================================
* TODO:
================================================================================
'''

import pymel.core as pm

class FTM_msCommandException(Exception):
    def __init__(self,message):
        self.message = '[FTM] '+message
    
    def __str__(self):
        return self.message

def FTM_getFluidElements( fluid ):
	if fluid is None:
		raise FTM_msCommandException('Please select a Fluid')

	fldTrs = None
	fldShp = None
	if pm.nodeType(fluid)== 'transform':
		childs = pm.listRelatives(s=True)
		if len(childs)>0 and pm.nodeType(childs[0]) == 'fluidShape' :
			fldTrs = fluid
			fldShp = childs[0]
		else :
			raise FTM_msCommandException('selection is invalid, you must select a fluid')
	elif pm.nodeType(fluid)== 'fluidShape':
		par = pm.listRelatives(p=True)
		if len(par)>0 and pm.nodeType(par[0]) == 'transform' :
			fldTrs = par[0]
			fldShp = fluid
		else :
			raise FTM_msCommandException('selection is invalid, you must select a fluid')
	else :
		raise FTM_msCommandException('selection is invalid, you must select a fluid')
	return (fldTrs,fldShp)

def FTM_createTransformedGeometry( objSrc, outShapeAtt, inShapeAtt, sourceTransform ):
	shps = pm.listRelatives(objSrc, s=True)
	srcShape = shps[0]

	dup = pm.duplicate(objSrc)
	shps = pm.listRelatives(dup[0], s=True)
	destShape = shps[0]
	dupShape = pm.parent(destShape, objSrc, add=True, s=True)
	pm.delete(dup[0])	
	destShape = dupShape[0] 

	trGeo = pm.createNode('transformGeometry')
	pm.connectAttr( sourceTransform+'.matrix', trGeo+'.transform')
	pm.connectAttr( srcShape+'.'+outShapeAtt,  trGeo+'.inputGeometry' )
	pm.connectAttr( trGeo+'.outputGeometry', destShape+'.'+inShapeAtt )
	pm.setAttr(srcShape+'.intermediateObject',True)
	return destShape

def FTM_createRulerPlane( control, axisPlane, isMainDirX, transformParent, dummyRulerTransform ):
	obj = pm.polyPlane( axis=axisPlane, ch=True, w=1, h=1, sx=1, sy=1 )
	if isMainDirX == True:
		bDir = 'width'
		bSubDir = 'subdivisionsWidth'
		sDir = 'height'
		sSubDir = 'subdivisionsHeight'
	else:
		sDir = 'width'
		sSubDir = 'subdivisionsWidth'
		bDir = 'height'
		bSubDir = 'subdivisionsHeight'
	
	pm.connectAttr( control+'.controlSize2', obj[1]+'.'+bDir)
	pm.connectAttr( control+'.rulerDivisions2', obj[1]+'.'+bSubDir)
	pm.connectAttr( control+'.rulerSmallSize', obj[1]+'.'+sDir)

	shapeTransformDriver = dummyRulerTransform
	if shapeTransformDriver is None:
		shapeTransformDriver = obj[0]
	outShp = FTM_createTransformedGeometry(obj[0], 'outMesh', 'inMesh', shapeTransformDriver )

	#shps = pm.listRelatives(obj[0],s=True)
	pm.connectAttr( control+'.rulerDisplay', outShp+'.visibility')
	pm.setAttr(outShp+'.template', 1)

	if transformParent is None:
		pm.parent(obj[0], control)
		return obj[0]
	else:
		pm.parent(outShp,transformParent, add=True, s=True)
		pm.delete( obj[0] )

def FTM_lockAndHide( obj, atts ):
	for att in atts:
		pm.setAttr(obj+'.'+att, lock=True, k=False)

def FTM_createNurbsCross( size, name, minSizeCtrlAtt, maxSizeCtrlAtt ):
	cv = pm.curve( p = [(-size,0,0), (size,0,0), (0,0,0), (0,size,0), (0,-size,0), (0,0,0), (0,0,size), (0,0,-size)], d=1, n=name)
	shps = pm.listRelatives(cv, s=True)

	if minSizeCtrlAtt is not None:
		pm.connectAttr( minSizeCtrlAtt, shps[0]+'.controlPoints[0].xValue' )
		pm.connectAttr( minSizeCtrlAtt, shps[0]+'.controlPoints[4].yValue' )
		pm.connectAttr( minSizeCtrlAtt, shps[0]+'.controlPoints[7].zValue' )
	if maxSizeCtrlAtt is not None:
		pm.connectAttr( maxSizeCtrlAtt, shps[0]+'.controlPoints[1].xValue' )
		pm.connectAttr( maxSizeCtrlAtt, shps[0]+'.controlPoints[3].yValue' )
		pm.connectAttr( maxSizeCtrlAtt, shps[0]+'.controlPoints[6].zValue' )

	return cv, shps[0]

def FTM_createNurbsCube( size, name, sizeCtrlAtts ):
	ptList = [(-size,-size,-size), (size,-size,-size), (size,-size,size), (-size,-size,size), (-size,-size,-size), (-size,size,-size), (size,size,-size), (size,size,size), (-size,size,size), (-size,size,-size), (size,size,-size),(size,-size,-size),(size,-size,size),(size,size,size),(-size,size,size),(-size,-size,size)]
	cv = pm.curve( p = ptList, d=1, n=name)
	shps = pm.listRelatives(cv, s=True)

	coordNames= ['xValue','yValue','zValue']
	#if minSizeCtrlAtt is not None:
	for i in range(len(ptList)):
		for j in range(3):
			if sizeCtrlAtts[j*2] is not None and ptList[i][j]<0 :
				pm.connectAttr( sizeCtrlAtts[j*2], shps[0]+'.controlPoints['+str(i)+'].'+coordNames[j] )
			if sizeCtrlAtts[j*2+1] is not None and ptList[i][j]>0 :
				pm.connectAttr( sizeCtrlAtts[j*2+1], shps[0]+'.controlPoints['+str(i)+'].'+coordNames[j] )

	return cv, shps[0]


def FTM_createNurbsCircle( size, axis, name ):
	circle = pm.circle( c=(0,0,0), nr=axis, sw=360, r=size, d=3, ut=False, s=8, ch=False)
	shps = pm.listRelatives(circle, s=True)
	return circle, shps[0]

def FTM_createImplodeController():
	implMain, implMainShp = FTM_createNurbsCross(.2,'fluidTextImplodeCtrl#',None,None)
	c0, cs0 = FTM_createNurbsCircle( .2, (1,0,0), 'cTemp#' )
	pm.parent(cs0, implMain, add=True, s=True)
	pm.delete( c0 )
	c1, cs1 = FTM_createNurbsCircle( .2, (0,1,0), 'cTemp#' )
	pm.parent(cs1, implMain, add=True, s=True)
	pm.delete( c1 )
	c2, cs2 = FTM_createNurbsCircle( .2, (0,0,1), 'cTemp#' )
	pm.parent(cs2, implMain, add=True, s=True)
	pm.delete( c2 )
	return implMain

def FTM_createRulerTransformGroup( fluidTransform, control, rulerTrans ):
	grpShapeTransform = pm.group(em=True,n='rulerShapeRotateTransform#')
	pm.parent(grpShapeTransform,rulerTrans, r=True )
	grpCtrlRotateCancel = pm.group(em=True,n='mainCtrlRotateCancel#')
	pm.parent(grpCtrlRotateCancel,rulerTrans, r=True )
	pm.orientConstraint(fluidTransform, grpCtrlRotateCancel)
	grpBaseRuler = pm.group(em=True,n='baseRulerRotate#')
	pm.parent(grpBaseRuler,grpCtrlRotateCancel, r=True )
	pm.connectAttr(rulerTrans+'.rotate',grpBaseRuler+'.rotate' )

	constraint = pm.orientConstraint(grpBaseRuler,grpShapeTransform )
	grpShapeTransform.addAttr('weight',k=True)
	pm.connectAttr( grpShapeTransform+'.weight', constraint+'.target[0].targetWeight', f=True)

	FTM_lockAndHide(grpCtrlRotateCancel, ['tx','ty','tz','sx','sy','sz','v'])
	FTM_lockAndHide(grpBaseRuler, ['tx','ty','tz','sx','sy','sz','v'])
	FTM_lockAndHide(grpShapeTransform, ['tx','ty','tz','sx','sy','sz','v'])

	return grpShapeTransform

def FTM_createBaseControl( fluidTransformParent ):
	sSize = 1
	bSize = 10.0
	bSize2 = 2.0*bSize
	cv = pm.curve( p = [(0,0,0), (bSize,0,0), (0,0,0), (0,bSize,0), (0,0,0), (0,0,bSize)], d=1, n='FT_RotateAndScaleCtrl#')
	cvChilds = pm.listRelatives( cv, s=True )

	cv.addAttr( 'controlSize', k=True, dv=bSize)
	cv.addAttr( 'rulerDisplay', k=True, at='bool',dv=False)
	cv.addAttr( 'rulerDivisions', k=True, at='long', dv=bSize2, min=1)
	cv.addAttr( 'rulerWidthMult', k=True, dv=2.0, min=0.0)

	# hidden secondary attribute
	cv.addAttr( 'controlSize2', k=False, dv=bSize2)
	cv.addAttr( 'rulerDivisions2', k=False, dv=bSize2)
	cv.addAttr( 'rulerSmallSize', k=False, dv=sSize)

	cv.addAttr( 'cubeDimMainMin', k=False, dv=5)
	cv.addAttr( 'cubeDimMainMax', k=False, dv=6)
	cv.addAttr( 'cubeDimSecMin', k=False, dv=-.5)
	cv.addAttr( 'cubeDimSecMax', k=False, dv=.5)


	pm.connectAttr( cv+'.controlSize', cvChilds[0]+'.controlPoints[1].xValue' )
	pm.connectAttr( cv+'.controlSize', cvChilds[0]+'.controlPoints[3].yValue' )
	pm.connectAttr( cv+'.controlSize', cvChilds[0]+'.controlPoints[5].zValue' )

	# ruler attribute calculations
	mult = pm.createNode('multDoubleLinear')
	pm.setAttr(mult+'.input2', 2.0)
	pm.connectAttr( cv+'.controlSize',mult+'.input1')
	pm.connectAttr( mult+'.output', cv+'.controlSize2')

	mult = pm.createNode('multDoubleLinear')
	pm.setAttr(mult+'.input2', 2.0)
	pm.connectAttr( cv+'.rulerDivisions',mult+'.input1')
	pm.connectAttr( mult+'.output', cv+'.rulerDivisions2')

	multDiv = pm.createNode('multiplyDivide')
	pm.setAttr( multDiv+'.operation', 2 )
	pm.connectAttr( cv+'.controlSize', multDiv+'.input1X')
	pm.connectAttr( cv+'.rulerDivisions', multDiv+'.input2X')

	mult = pm.createNode('multDoubleLinear')
	pm.connectAttr( cv+'.rulerWidthMult',mult+'.input1')
	pm.connectAttr( multDiv+'.outputX',mult+'.input2')
	pm.connectAttr( mult+'.output', cv+'.rulerSmallSize')

	# Rulers
	transformRuler = pm.group(em=True, n='ruler#')
	pm.parent(transformRuler,cv,r=True)
	# there is a special transform on the shape to have 2 spaces possible for the shape
	# rotateSpace=parent the rulers is rotated by the main Control like a jormal child
	# rotateSpace=free the rulers is independant from the main Control rotation
	grpDummyTransformRuler = FTM_createRulerTransformGroup( fluidTransformParent, cv, transformRuler )
	FTM_createRulerPlane( cv, (0,1,0), True, transformRuler, grpDummyTransformRuler )
	FTM_createRulerPlane( cv, (0,1,0), False, transformRuler, grpDummyTransformRuler )
	FTM_createRulerPlane( cv, (1,0,0), True, transformRuler, grpDummyTransformRuler )
	FTM_createRulerPlane( cv, (1,0,0), False, transformRuler, grpDummyTransformRuler )
	FTM_createRulerPlane( cv, (0,0,1), True, transformRuler, grpDummyTransformRuler )
	FTM_createRulerPlane( cv, (0,0,1), False, transformRuler, grpDummyTransformRuler )
	transformRuler.addAttr( 'rotateSpace', at='enum', en='parent:free:', k=True)
	pm.connectAttr(transformRuler+'.rotateSpace', grpDummyTransformRuler+'.weight')
	FTM_lockAndHide(transformRuler, ['tx','ty','tz','sx','sy','sz','v'])

	#nurbs cube attribute size calculations
	mult1 = pm.createNode('multDoubleLinear')
	pm.setAttr(mult1+'.input2', 0.5)
	pm.connectAttr( cv+'.rulerSmallSize',mult1+'.input1')
	pm.connectAttr( mult1+'.output', cv+'.cubeDimSecMax')

	mult2 = pm.createNode('multDoubleLinear')
	pm.setAttr(mult2+'.input2', -0.5)
	pm.connectAttr( cv+'.rulerSmallSize',mult2+'.input1')
	pm.connectAttr( mult2+'.output', cv+'.cubeDimSecMin')

	add = pm.createNode('addDoubleLinear')
	pm.connectAttr( cv+'.controlSize',add+'.input2')
	pm.connectAttr( cv+'.rulerSmallSize',add+'.input1')
	pm.connectAttr( add+'.output', cv+'.cubeDimMainMax')

	pm.connectAttr( cv+'.controlSize', cv+'.cubeDimMainMin')

	# nurbs Cube boxes added to main control
	# XAxis cube
	cubeTra, cubeShp = FTM_createNurbsCube( 1.0,'tempAxisCube#', [cv+'.cubeDimMainMin', cv+'.cubeDimMainMax', cv+'.cubeDimSecMin', cv+'.cubeDimSecMax', cv+'.cubeDimSecMin', cv+'.cubeDimSecMax' ] )
	pm.parent(cubeShp,cv,s=True,add=True)
	pm.delete(cubeTra)
	#YAxis cube
	cubeTra, cubeShp = FTM_createNurbsCube( 1.0,'tempAxisCube#', [cv+'.cubeDimSecMin', cv+'.cubeDimSecMax', cv+'.cubeDimMainMin', cv+'.cubeDimMainMax',  cv+'.cubeDimSecMin', cv+'.cubeDimSecMax' ] )
	pm.parent(cubeShp,cv,s=True,add=True)
	pm.delete(cubeTra)
	#ZAxis cube
	cubeTra, cubeShp = FTM_createNurbsCube( 1.0,'tempAxisCube#', [cv+'.cubeDimSecMin', cv+'.cubeDimSecMax', cv+'.cubeDimSecMin', cv+'.cubeDimSecMax', cv+'.cubeDimMainMin', cv+'.cubeDimMainMax' ] )
	pm.parent(cubeShp,cv,s=True,add=True)
	pm.delete(cubeTra)

	FTM_lockAndHide(cv, ['tx','ty','tz','v'])

	pm.parent(cv, fluidTransformParent, r=True)

	return cv

def FTM_insertController( driverObj, driverAtt, destAttribute, sourceAttributeForRedirectValue=None, invert=False ):
	newDriver = driverObj+'.'+driverAtt
	inConns = pm.listConnections(destAttribute, s=True,d=False, p=True)

	attributeToApplyDrivenValue = newDriver
	if sourceAttributeForRedirectValue is not None:
		attributeToApplyDrivenValue = sourceAttributeForRedirectValue

	if len(inConns) == 0:
		val = pm.getAttr(destAttribute)
		if invert == False :
			pm.setAttr( attributeToApplyDrivenValue, val)
		else:
			pm.setAttr( attributeToApplyDrivenValue, -1*val)
	else:
		if invert is False:
			pm.connectAttr( inConns[0], attributeToApplyDrivenValue)
		else :
			invDriverAtt = 'inv_'+driverAtt
			driverObj.addAttr(invDriverAtt, k=True)
			pm.connectAttr( inConns[0], invDriverAtt)
			multDiv = pm.createNode('multiplyDivide')
			pm.setAttr(multDiv+'.input2X', -1)
			pm.connectAttr(invDriverAtt, multDiv+'.input1X')
			pm.connectAttr( multDiv+'.outputX', attributeToApplyDrivenValue )
			#pm.connectAttr( inConns[0], newDriver)
		pm.disconnectAttr( inConns[0], destAttribute)

	if invert is False:
		pm.connectAttr( newDriver, destAttribute )
	else:
		multDiv = pm.createNode('multiplyDivide')
		pm.setAttr( multDiv+'.operation', 1 )
		pm.setAttr(multDiv+'.input2X', -1)
		pm.connectAttr(newDriver, multDiv+'.input1X')
		pm.connectAttr( multDiv+'.outputX', destAttribute )


def FTM_setupFluidForceRefresh ( fluidShape,  atts ):
	import re
	conns = pm.listConnections( fluidShape+'.voxelQuality', s=True, d=False, p=False  )
	expr = None
	text = None
	attributesTrigger = atts[:] #shallow copy

	if conns is not None and len(conns)>0 and fluidShape.hasAttr('voxelQualityChooser') :
		if pm.objectType( conns[0], isType='expression' ) == False:
			raise FTM_msCommandException('The fluid [ '+fluidShape+' ] has an incoming connection in attribute voxelQuality, unable to setup a refresh expression')
		expr = conns[0]
		text = pm.expression( expr, q=True, s=True)
	else:
		if len(conns)>0:
			raise FTM_msCommandException('The fluid [ '+fluidShape+' ] has an incoming connection in attribute voxelQuality, unable to setup a refresh expression')
		if fluidShape.hasAttr('voxelQualityChooser') == False:
			current = pm.getAttr( fluidShape+'.voxelQuality' )
			fluidShape.addAttr( 'voxelQualityChooser',  k=True, at='enum', en='faster=1:better=2', dv=current)

	if text is not None:
		#let's gather the trigger of refresh inside the expression
		matches = re.findall(r'.*?\$trigs\[size\(\$trigs\)\]=(.*?);', text )  #$triggers[0]=.I[0];
		for m in matches:
			if re.match( r'\.I\[[0-9]+?\]', m) is None:
				attributesTrigger.append(m)
	text  = '// Fluid display Refresh expression\n'
	text += '// you can add triggers here but you have to follow the current syntax\n'
	text += 'float $trigs[];clear $trigs;\n\n'
	for i in range(len(attributesTrigger)):
		text += '$trigs[size($trigs)]='+attributesTrigger[i]+';\n'
	text += '\n//Result\n'
	text += 'voxelQuality = voxelQualityChooser;\n'
	if expr :
		pm.expression( expr, e=True, s=text, o=fluidShape, ae=True)
	else:
		pm.expression( s=text, o=fluidShape, ae=False, n='forceFluidDisplayRefreshExpr#')

def FTM_addFluidTextureManipulators( fluid ):
	'''
	create manipulators for the texture parameters of a fluid
	the parameter fluid can be a fluid Transform or a fluidShape
	return the main control (rotate and scale), the texture origin control, the implode position control, the origin position offset, the root group of the rig
	'''

	(ft,fs) = FTM_getFluidElements(fluid)

	# global group root
	grpRoot = pm.group(em=True, n='fluidTextureManipulators#')
	FTM_lockAndHide(grpRoot, ['tx','ty','tz','rx','ry','rz','sx','sy','sz'])

	# group with fluid transformation
	grp = pm.group(em=True, n='fluidTransformSpace#')
	pCstRes = pm.parentConstraint(ft,grp)
	sCstRes = pm.scaleConstraint(ft,grp)
	FTM_lockAndHide(grp, ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'])
	pm.parent(grp,grpRoot,r=True)


	# main control for scale and rotate of the texture
	control = FTM_createBaseControl(grp)

	# group with the space operation requiered to match the coordinate in the fluid texture and also deal with the frequency space
	grpTextureSpaceMatch = pm.group(em=True, n='fluidTextureMatchSpace#')
	grpTextureSpaceMatch.addAttr('freqOnOff',k=False)
	condFreq = pm.createNode('condition')
	pm.connectAttr(grpTextureSpaceMatch+'.freqOnOff', condFreq+'.firstTerm')
	pm.setAttr(condFreq+'.secondTerm', .5)
	pm.setAttr(condFreq+'.operation',4)
	pm.setAttr(condFreq+'.colorIfTrueR',1.0)
	pm.setAttr(condFreq+'.colorIfFalseG',1.0)
	pm.connectAttr(fs+'.frequency', condFreq+'.colorIfFalseR')
	pm.connectAttr(fs+'.frequency', condFreq+'.colorIfTrueG')

	pm.parent(grpTextureSpaceMatch, control, r=True)
	multDiv = pm.createNode('multiplyDivide')
	pm.setAttr( multDiv+'.operation', 2 )
	pm.setAttr(multDiv+'.input1X', -80.0)
	pm.connectAttr( condFreq+'.outColorR', multDiv+'.input2X')
	pm.connectAttr( multDiv+'.outputX', grpTextureSpaceMatch+'.sx')
	pm.connectAttr( multDiv+'.outputX', grpTextureSpaceMatch+'.sy')
	pm.connectAttr( multDiv+'.outputX', grpTextureSpaceMatch+'.sz')
	# we create an inverse scale to maintain the size of the translate controller when frequency change
	grpTextureSpaceMatch.addAttr('invScale',k=False)
	grpTextureSpaceMatch.addAttr('invScaleMinus',k=False)
	grpTextureSpaceMatch.addAttr('invScaleDiv2', k=False) # for the box, box is using the dimensions of the cross divided by 2
	grpTextureSpaceMatch.addAttr('invScaleMinusDiv2', k=False)
	multDivInv = pm.createNode('multiplyDivide')
	pm.setAttr( multDivInv+'.operation', 2 )
	pm.connectAttr( condFreq+'.outColorR', multDivInv+'.input1X')
	pm.connectAttr( condFreq+'.outColorR', multDivInv+'.input1Y')
	pm.setAttr(multDivInv+'.input2X', 80.0)
	pm.setAttr(multDivInv+'.input2Y', -80.0)
	pm.connectAttr( multDivInv+'.outputX', grpTextureSpaceMatch+'.invScale')
	pm.connectAttr( multDivInv+'.outputY', grpTextureSpaceMatch+'.invScaleMinus')

	multDivDiv2 = pm.createNode('multiplyDivide')
	pm.connectAttr( grpTextureSpaceMatch+'.invScale', multDivDiv2+'.input1X')
	pm.connectAttr( grpTextureSpaceMatch+'.invScaleMinus', multDivDiv2+'.input1Y')
	pm.setAttr(multDivDiv2+'.input2X', 0.5)
	pm.setAttr(multDivDiv2+'.input2Y', 0.5)
	pm.connectAttr( multDivDiv2+'.outputX', grpTextureSpaceMatch+'.invScaleDiv2')
	pm.connectAttr( multDivDiv2+'.outputY', grpTextureSpaceMatch+'.invScaleMinusDiv2')

	FTM_lockAndHide(grpTextureSpaceMatch, ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'])


	# offset to help position the translate helper
	gpOffs = pm.group(em=True,n='fluidTextTranslateOFFSET#')
	FTM_lockAndHide(gpOffs, ['sx','sy','sz','rx','ry','rz','v'])
	pm.parent(gpOffs,grpTextureSpaceMatch,r=True)

	# texture translate controller under the translate offset (depending if we want to have coordinate dependent of frequency or not we change the output)
	# if the mode is frequencyDependent then the translate values of this control are exactly the values that are put into textureOrigin
	# but if we want to be independent of the frequency then it is a multiply of the coordinate and of frequency
	origCtrl, origCtrlShp = FTM_createNurbsCross(1.0,'FT_OriginCtrl#',grpTextureSpaceMatch+'.invScaleMinus',grpTextureSpaceMatch+'.invScale')
	origCtrl.addAttr('frequencyDependentSpace',at='bool',dv=True,k=True)
	origCtrl.addAttr('outputPosition',at='double3',k=True)
	origCtrl.addAttr('outputPositionX', at='double', p='outputPosition')	
	origCtrl.addAttr('outputPositionY', at='double', p='outputPosition')	
	origCtrl.addAttr('outputPositionZ', at='double', p='outputPosition')
	multDivTranslateAndFreq = pm.createNode('multiplyDivide')
	pm.connectAttr(origCtrl+'.translate',multDivTranslateAndFreq+'.input1')
	pm.connectAttr(condFreq+'.outColorG',multDivTranslateAndFreq+'.input2X')
	pm.connectAttr(condFreq+'.outColorG',multDivTranslateAndFreq+'.input2Y')
	pm.connectAttr(condFreq+'.outColorG',multDivTranslateAndFreq+'.input2Z')
	pm.connectAttr(multDivTranslateAndFreq+'.output',origCtrl+'.outputPosition')

	nCube, nCubeShp = FTM_createNurbsCube(1.0,'fluidTextTranslateCtrlCube#', [grpTextureSpaceMatch+'.invScaleMinusDiv2',grpTextureSpaceMatch+'.invScaleDiv2',grpTextureSpaceMatch+'.invScaleMinusDiv2',grpTextureSpaceMatch+'.invScaleDiv2',grpTextureSpaceMatch+'.invScaleMinusDiv2',grpTextureSpaceMatch+'.invScaleDiv2'])
	pm.parent(nCubeShp,origCtrl,s=True,add=True)
	pm.delete(nCube)

	pm.connectAttr(origCtrl+'.frequencyDependentSpace', grpTextureSpaceMatch+'.freqOnOff')
	FTM_lockAndHide(origCtrl, ['rx','ry','rz'])
	pm.parent(origCtrl, gpOffs, r=True)

	# now the implode controller under the main control (implode is not frequency dependent and is not textureScale dependent BUT it is textureRotate dependent)
	grpImplSpace = pm.group(em=True,n='FT_ImplSpace#')
	pm.setAttr(grpImplSpace+'.scale', (5,5,5))
	pm.connectAttr( control+'.rotateX', grpImplSpace+'.rotateX'  )
	pm.connectAttr( control+'.rotateY', grpImplSpace+'.rotateY'  )
	pm.connectAttr( control+'.rotateZ', grpImplSpace+'.rotateZ'  )
	FTM_lockAndHide(grpImplSpace, ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v'] )
	impl = FTM_createImplodeController()
	FTM_lockAndHide(impl, ['rx','ry','rz'] )
	pm.parent(impl,grpImplSpace,r=True)
	pm.parent(grpImplSpace,grp,r=True)

	# do the actual connections from the controllers to the fluid texture parameters (reconnect any in-connections already on the fluid parameters)
	FTM_insertController( origCtrl,'outputPosition.outputPositionX', fs+'.textureOriginX', origCtrl+'.translateX' )
	FTM_insertController( origCtrl,'outputPosition.outputPositionY', fs+'.textureOriginY', origCtrl+'.translateY' )
	FTM_insertController( origCtrl,'outputPosition.outputPositionZ', fs+'.textureOriginZ', origCtrl+'.translateZ')	

	FTM_insertController( control,'scaleX', fs+'.textureScaleX' )
	FTM_insertController( control,'scaleY', fs+'.textureScaleY' )
	FTM_insertController( control,'scaleZ', fs+'.textureScaleZ' )

	FTM_insertController( control,'rotateX', fs+'.textureRotateX' )
	FTM_insertController( control,'rotateY', fs+'.textureRotateY' )
	FTM_insertController( control,'rotateZ', fs+'.textureRotateZ' )

	FTM_insertController( impl,'translateX', fs+'.implodeCenterX')
	FTM_insertController( impl,'translateY', fs+'.implodeCenterY')
	FTM_insertController( impl,'translateZ', fs+'.implodeCenterZ')

	# add an expression to force the refresh of the display of the fluid when the maipulators change
	FTM_setupFluidForceRefresh( fs, [control+'.sx', control+'.sy', control+'.sz', control+'.rx', control+'.ry', control+'.rz', origCtrl+'.tx', origCtrl+'.ty', origCtrl+'.tz', impl+'.tx', impl+'.ty', impl+'.tz'] )

	return control, origCtrl, impl, gpOffs, grpRoot


if __name__ == "__main__":
	try:
		sel = pm.ls(sl=True)
		if not len(sel):
			raise FTM_msCommandException('Please select a fluid')
		FTM_addFluidTextureManipulators( sel[0])
	except FTM_msCommandException, e:
		pm.mel.error( e.message)