import cv2 as cv
import numpy as np
import py2 #arquivo que contem funcoes 
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

global ans
ans=True

def char_position(letter):
        return ord(letter) - 97

def send():
    global respostas
    global root
    global myEntryBox
    opcoes = myEntryBox.get()
    posicoes=[]
    opcoes = opcoes.split()
    for indx in range(len(opcoes)):
        posicao = char_position(opcoes[indx])
        posicoes.append(posicao)
    respostas = posicoes
    print('respostas: ',respostas)
    root.destroy()

## Definir respostas corretas
respostas = []
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
    caminhoImagem = str(path.absolute()) + '//imagens//'

    fileImage = filedialog.askopenfilename(initialdir=caminhoImagem)

    img = cv.imread(fileImage)
    print(img)

    #definir tamanho de imagem e aplica
    widthImg = 510
    heightImg = 700

    questoes = 5
    opcoes = 5
    numAcertos = 0
    porcentagemAcerto = 0
    myIndex=[]


    img = cv.resize(img, (widthImg, heightImg))

    #pré-processamento
    imgCnt= img.copy() #copia imagem original
    imgBiggestContours = img.copy() #copia imagem original
    imgCinza = cv.cvtColor(img, cv.COLOR_BGR2GRAY) #escala de cinza
    imgBlur = cv.GaussianBlur(imgCinza, (5, 5), 5) #efeito glaussiano #imagem, tamanho do núcleo, sigma X
    imgCanny = cv.Canny(imgBlur, 10, 50) #threshold 

    #encontrando os contornos na imagem
    countours, hierarchy = cv.findContours(imgCanny, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)
    cv.drawContours(imgCnt, countours, -1, (0, 255,0), 10)

    #Encontrando os maiores CONTORNOS
    rectCon = py2.rectContour(countours)
    biggestContour = py2.getCornerPoints(rectCon[0])#PONTOS DA AREA DE RESPOSTAS
    print(len(biggestContour))

    #AO ENCONTRAR CONTORNOS E PONTOS DE AREAS
    if biggestContour.size !=0:

        # BIGGEST RECTANGLE WARPING
        biggestContour = py2.reorder(biggestContour)
        cv.drawContours(imgBiggestContours,biggestContour,-1,(0,255,0),20)# DRAW THE BIGGEST CONTOUR
        pts1 = np.float32(biggestContour) # PREPARE POINTS FOR WARP
        pts2 = np.float32([[0, 0],[widthImg, 0], [0, heightImg],[widthImg, heightImg]]) # PREPARE POINTS FOR WARP
        matrix = cv.getPerspectiveTransform(pts1, pts2) # GET TRANSFORMATION MATRIX
        imgWarpColored = cv.warpPerspective(img, matrix, (widthImg, heightImg)) # APPLY WARP PERSPECTIVE

        # APPLY THRESHOLD
        imgWarpGray = cv.cvtColor(imgWarpColored,cv.COLOR_BGR2GRAY) # CONVERTE PARA ESCALA DE CINZA
        imgThresh = cv.threshold(imgWarpGray, 140, 255,cv.THRESH_BINARY_INV )[1] # APPLY THRESHOLD AND INVERSE

        boxes = py2.splitBoxes(imgThresh) #todos os "circulos" do gabarito

        #conta a intensidade dos pixel para cada opcoes do questionario
        pixels = np.zeros((questoes, opcoes))
        countCol = 0 
        countLin = 0
        
        for image in boxes:
            totalPixels = cv.countNonZero(image)
            pixels[countLin][countCol] = totalPixels
            countCol +=1
            if(countCol == opcoes): countLin += 1 ;countCol=0 
        print(pixels)

        #atraves do pixel maximo define qual opcao foi marcada exibindo o índice entre 0 a 4 (5 questoes)
        myIndex = []
        for x in range (0, questoes) : 
            array = pixels[x]
            myIndexValor = np.where(array==np.amax(array))
            myIndex.append(myIndexValor[0][0])

        
        print(myIndex) #exibe o índice das opcoes de cada questao marcada
        
        ##verifica porcentagem de acerto
        for index in range(len(myIndex)):
            if respostas[index] == myIndex[index]:
                numAcertos+=1

        porcentagemAcento=0

        if numAcertos > 0:
            porcentagemAcerto = (numAcertos * 100) / questoes  

    

    ## adiciona texto a imagem
    imagemtexto = img.copy()
    txtResultado =  "Resultado=" + str(porcentagemAcerto) + '%'
    cv.putText(imagemtexto,txtResultado, (10, 500), cv.QT_FONT_BLACK, 2, (0, 255, 255), 2)


    imgBlank = np.zeros_like(img)
    #ADICIONANDO IMAGENS EM UM ARRAY
    imgArray = ([img, imgCinza, imgBlur, imgCanny],  [imgCnt, imgBiggestContours, imgWarpColored, imgThresh], [imagemtexto,imgBlank,imgBlank,imgBlank])
    #CHAMANDO A FUNCAO PARA EMPILHAR AS IMAGENS
    imgStacked = py2.empilharImagens(imgArray, 0.5) 

    #mostra janela com a imagem original
    cv.imshow('Imagens', imgStacked)

    ''' #MOSTRAR QUAIS QUESTOES FORAM ACERTADAS.
    strQ=" "
    questoesAcertadas = []
    for i in range (0, 4) : 
        if myIndex[i]==respostas[i]:
            questoesAcertadas.append(myIndex[i])
            num=questoesAcertadas[i]+1
            strQ+=str(num)+" "
            print(strQ)
        
    '''

    #exibe o resultado
    messagebox.showinfo(title="NOTA", message=str(porcentagemAcerto)+"%")

   
    # 
    ans = messagebox.askyesnocancel(title="Outra correção", message="Gostaria de fazer outra correção?")

    if ans:
        cv.destroyAllWindows()

cv.waitKey(0)
