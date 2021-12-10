import cv2 as cv
import numpy as np
import functions #arquivo que contem funcoes 
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter import *


global ans
ans=True

def char_position(letter):
        return ord(letter) - 97

def send():
    global responses
    global root
    global myEntryBox
    opcoes = myEntryBox.get()
    posicoes=[]
    opcoes = opcoes.split()
    for indx in range(len(opcoes)):
        posicao = char_position(opcoes[indx])
        posicoes.append(posicao)
    responses = posicoes
    print('respostas: ',responses)
    root.destroy()

## Definir respostas corretas
responses = []
root = tk.Tk()
myLabel = tk.Label(root, text='\n\nInsira as respostas do gabarito a partir do numero de questões: Ex.(b c a d c)\n\n')
myLabel.pack()
myEntryBox = tk.Entry(root)
myEntryBox.pack()
mySubmitButton = tk.Button(root, text='Salvar', command=send)
mySubmitButton.pack()

root.mainloop()


while(ans):
    ##Caminho da imagem
    path = Path(sys.path[0])
    pathImage = str(path.absolute()) + '//imagens//'

    root = Tk()
    root.withdraw()
    fileImage = askopenfilename(initialdir=pathImage)
    root.destroy()

    #fileImage = filedialog.askopenfilename(initialdir=pathImage)

    img = cv.imread(fileImage)
    #print(img)

    #definir tamanho de imagem e aplica
    widthImg = 510
    heightImg = 700

    questions = 5
    options = 5
    numHits = 0
    percentHits = 0
    myIndex=[]


    img = cv.resize(img, (widthImg, heightImg))

    #pré-processamento
    imgCnt= img.copy() #copia imagem original
    imgBiggestContours = img.copy() #copia imagem original
    
    imgGray = cv.cvtColor(img, cv.COLOR_BGR2GRAY) #escala de cinza
    imgBlur = cv.GaussianBlur(imgGray, (5, 5), 5) #efeito glaussiano #imagem, tamanho do núcleo, sigma X
    imgCanny = cv.Canny(imgBlur, 10, 50) #threshold 

    #encontrando os contornos na imagem
    countours, hierarchy = cv.findContours(imgCanny, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
    cv.drawContours(imgCnt, countours, -1, (0, 255,0), 10)

    #Encontrando os maiores CONTORNOS
    rectCon = functions.rectContour(countours)
    biggestContour = functions.getCornerPoints(rectCon[0])#PONTOS DA AREA DE RESPOSTAS

    #AO ENCONTRAR CONTORNOS E PONTOS DE AREAS
    if biggestContour.size !=0:

        # MAIOR RETÂNGULO
        biggestContour = functions.reorder(biggestContour)
        cv.drawContours(imgBiggestContours,biggestContour,-1,(0,255,0),20)# DESENHE O MAIOR CONTORNO
        pts1 = np.float32(biggestContour) # PREPARAR PONTOS
        pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARAR PONTOS
        matrix = cv.getPerspectiveTransform(pts1, pts2) # OBTER MATRIZ DE TRANSFORMAÇÃO
        imgWarpColored = cv.warpPerspective(img, matrix, (widthImg, heightImg)) # APLICAR A PERSPECTIVA

        # APLICAR THRESHOLD
        imgWarpGray = cv.cvtColor(imgWarpColored,cv.COLOR_BGR2GRAY) # CONVERTE PARA ESCALA DE CINZA
        imgThresh = cv.threshold(imgWarpGray, 140, 255,cv.THRESH_BINARY_INV )[1] # APLICAR THRESHOLD E INVERSO

        boxes = functions.splitBoxes(imgThresh) #todos os "circulos" do gabarito

        #conta a intensidade dos pixel para cada opcoes do questionario
        pixels = np.zeros((questions, options))
        countCol = 0 
        countLin = 0
        
        for image in boxes:
            totalPixels = cv.countNonZero(image)
            pixels[countLin][countCol] = totalPixels
            countCol +=1
            if(countCol == options): countLin += 1 ;countCol=0 
        print("Pixels")
        print(pixels)

        #atraves do pixel maximo define qual opcao foi marcada exibindo o índice entre 0 a 4 (5 questoes)
        myIndex = []
        for x in range (0, questions) : 
            array = pixels[x]
            myIndexValor = np.where(array==np.amax(array))
            myIndex.append(myIndexValor[0][0])

        
        print(myIndex) #exibe o índice das opcoes de cada questao marcada
        
        ##verifica porcentagem de acerto
        for index in range(len(myIndex)):
            if responses[index] == myIndex[index]:
                numHits+=1

        porcentagemAcento=0

        if numHits > 0:
            percentHits = (numHits * 100) / questions  

    #MOSTRAR QUAIS QUESTOES FORAM ACERTADAS.
    strQ=""
    questoesAcertadas = []
    contador=0
    for i in range (0, 5): 
         if myIndex[i]==responses[i]:
            questoesAcertadas.append(myIndex[i])
            num=questoesAcertadas[contador]+1
            contador+=1
            strQ+=str(num)+" " 
    
    #exibe o resultado
    root = Tk()
    root.withdraw()
    messagebox.showinfo(title="NOTA", message=str(percentHits)+"%\nQuestões corretas: "+strQ)
    ans = messagebox.askyesnocancel(title="Outra correção", message="Gostaria de fazer outra correção?")
    root.destroy()

    if ans:
        cv.destroyAllWindows()



## adiciona texto a imagem
imagemtexto = img.copy()
txtResultado =  "Resultado=" + str(percentHits) + '%'
cv.putText(imagemtexto,txtResultado, (10, 500), cv.QT_FONT_BLACK, 2, (0, 255, 255), 2)
imgBlank = np.zeros_like(img)
#ADICIONANDO IMAGENS EM UM ARRAY
imgArray = ([img, imgGray, imgBlur],  [imgCanny, imgCnt, imgBiggestContours], [imgWarpColored, imgThresh, imagemtexto])
#CHAMANDO A FUNCAO PARA EMPILHAR AS IMAGENS
imgStacked = functions.imageStack(imgArray, 0.4) 
#mostra janela com a imagem original
cv.imshow('Imagens', imgStacked)

cv.waitKey(0)
