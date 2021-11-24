import cv2 as cv
import numpy as np
import py2 #arquivo que contem funcoes 
import sys
from pathlib import Path

path = Path(sys.path[0])
caminhoImagem = str(path.absolute()) + '//imagens//'

img = cv.imread(caminhoImagem + "Q1.1.jpeg")
print(img)
#definir tamanho de imagem e aplica
widthImg = 510
heightImg = 700
img = cv.resize(img, (widthImg, heightImg))

#pré-processamento
imgCnt= img.copy() #copia imagem original
imgBiggestContours = img.copy() #copia imagem original
imgCinza = cv.cvtColor(img, cv.COLOR_BGR2GRAY) #escala de cinza
imgBlur = cv.GaussianBlur(imgCinza, (5, 5), 1) #efeito glaussiano #imagem, tamanho do núcleo, sigma X
imgCanny = cv.Canny(imgBlur, 10, 50) #threshold 

#encontrando os contornos na imagem
countours, hierarchy = cv.findContours(imgCanny, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
cv.drawContours(imgCnt, countours, -1, (0, 255,0), 10)

#Encontrando retangulos
rectCon = py2.rectContour(countours)
biggestContour = py2.getCornerPoints(rectCon[0])
gradePoints = py2.getCornerPoints(rectCon[8])
print(len(biggestContour))

if biggestContour.size !=0 and gradePoints.size != 0:

    # BIGGEST RECTANGLE WARPING
    biggestContour = py2.reorder(biggestContour)
    cv.drawContours(imgBiggestContours,biggestContour,-1,(0,255,0),20)# DRAW THE BIGGEST CONTOUR
    gradePoints = py2.reorder(gradePoints)
    pts1 = np.float32(biggestContour) # PREPARE POINTS FOR WARP
    pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARE POINTS FOR WARP
    matrix = cv.getPerspectiveTransform(pts1, pts2) # GET TRANSFORMATION MATRIX
    imgWarpColored = cv.warpPerspective(img, matrix, (widthImg, heightImg)) # APPLY WARP PERSPECTIVE

    # SECOND BIGGEST RECTANGLE WARPING
    cv.drawContours(imgBiggestContours,gradePoints,-1,(255,0,0),20) # DRAW THE BIGGEST CONTOUR
    gradePoints = py2.reorder(gradePoints) # REORDER FOR WARPING
    ptsG1 = np.float32(gradePoints)  # PREPARE POINTS FOR WARP
    ptsG2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])  # PREPARE POINTS FOR WARP
    matrixG = cv.getPerspectiveTransform(ptsG1, ptsG2)# GET TRANSFORMATION MATRIX
    imgGradeDisplay = cv.warpPerspective(img, matrixG, (325, 150)) # APPLY WARP PERSPECTIVE
    cv.imshow("Grade",imgGradeDisplay)

     # APPLY THRESHOLD
    imgWarpGray = cv.cvtColor(imgWarpColored,cv.COLOR_BGR2GRAY) # CONVERT TO GRAYSCALE
    imgThresh = cv.threshold(imgWarpGray, 140, 255,cv.THRESH_BINARY_INV )[1] # APPLY THRESHOLD AND INVERSE

    py2.splitBoxes(imgThresh)



imgBlank = np.zeros_like(img)
#ADICIONANDO IMAGENS EM UM ARRAY
imgArray = ([img, imgCinza, imgBlur, imgCanny],  [imgCnt, imgBiggestContours, imgWarpColored, imgThresh])
#CHAMANDO A FUNCAO PARA EMPILHAR AS IMAGENS
imgStacked = py2.empilharImagens(imgArray, 0.5) 

#mostra janela com a imagem original
cv.imshow('Imagens', imgStacked)


cv.waitKey(0)
