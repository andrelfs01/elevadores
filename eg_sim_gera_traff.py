import numpy as np 
# parâmetros do sistema
Nf, Nc = 16, 4 # floors, cars
# car state:
cp = np.zeros(Nc,dtype=int) # car position [0,30*Nf]
cm = np.zeros(Nc,dtype=int) # car moviment state [0,1,2,3,4,5]
cd = np.zeros(Nc,dtype=int) # car actual destination [0,Nf-1]
cb = np.zeros([Nc,Nf],dtype=bool) # car botons
ct = np.zeros(Nc,dtype=int) # stop car time
cL = [[] for i in range(Nc)]   # listas de embarcados
# floor state:
fb = np.zeros([Nf,2],dtype=bool) # floor botons 
ftpc = np.zeros(Nf) # tempo da próxima chegada de passageiro naquele piso
fq = [[] for i in range(Nf)]   # filas de piso
Listp = []  # lista de processados
ent_id = 0   # id de entidade passageiro
# simulação:
import json
with open('traff_poisson.txt', 'r') as f:
    traff_poisson = json.loads(f.read())
with open('traff_up.txt', 'r') as f:
    traff_up = json.loads(f.read())
with open('traff_dp.txt', 'r') as f:
    traff_dp = json.loads(f.read())
with open('traff_du.txt', 'r') as f:
    traff_du = json.loads(f.read())
#
traff = traff_dp
cm[:] = 5
cd[:] = 15
Ts = 3600
#lamb = 0.021  # chega um por floor a cada 50 s 
ent_p = []
for fc in range(Nf):
    ent_p.append(traff[fc].pop())
    ftpc[fc] = ent_p[fc][1]
#
for ts in range(Ts):
# PROCESSA CHEGADAS
    for fc in range(Nf): # processa chegadas
        if ftpc[fc] < ts:
            fq[fc].append(ent_p[fc])
            if ent_p[fc][4] > fc:
                fb[fc][1] = True
            elif ent_p[fc][4] < fc:
                fb[fc][0] = True
            ent_p[fc] = traff[fc].pop()
            ftpc[fc] = ent_p[fc][1]
# CONTROLADOR DO GRUPO DE ELEVADORES - BASELINE
    for fc in range(Nf): # procura por um piso não atribuido.
        if fb[fc][1] == True:
            caminho = 0
            for cc in range(Nc): # já tem um car a caminho?
                if cp[cc] < fc and cm[cc] == 5 and cd[cc] >= fc:
                    caminho = 1
            if caminho == 0:
                for cc in range(Nc):
                    if cp[cc] < fc and cm[cc] == 5 and cd[cc] < fc:
                        cd[cc] = fc
                        caminho = 1
                        break
            if caminho == 0:
                for cc in range(Nc):
                    if cm[cc] == 3:
                        cd[cc] = fc
                        caminho = 1
                        if cp[cc] <= fc:
                            cm[cc] = 5
                            break
                        if cp[cc] > fc:
                            cm[cc] = 4
                            break
##           
        if fb[fc][0] == True:
            caminho = 0
            for cc in range(Nc): # já tem um car a caminho?
                if cp[cc] > fc and cm[cc] == 4 and cd[cc] <= fc:
                    caminho = 1
            if caminho == 0:
                for cc in range(Nc):
                    if cp[cc] > fc and cm[cc] == 4 and cd[cc] > fc:
                        cd[cc] = fc
                        caminho = 1
                        break
            if caminho == 0:
                for cc in range(Nc):
                    if cm[cc] == 3:
                        cd[cc] = fc
                        caminho = 1
                        if cp[cc] >= fc:
                            cm[cc] = 4
                            break
                        else:
                            cm[cc] = 5
                            break
##
# PROCESSA CARROS
    for cc in range(Nc): # processa carros
        floor, entre_floor = np.divmod(cp[cc],3)
        if entre_floor != 0: # carro fora de um floor
            if cm[cc] == 0: # carro bloqueado - fora de serviço
                cm[cc] = 0
            elif cm[cc] == 1: # parado durante viagem para baixo
                print('error1')
            elif cm[cc] == 2: # parado durante viagem para cima
                print('error2')
            elif cm[cc] == 3: # parado ocioso - sem missão atribuída
                cm[cc] = 3
            elif cm[cc] == 4: # viajando para baixo
                if cp[cc] > 0:
                    cp[cc] = cp[cc] - 1
            elif cm[cc] == 5: # viajando para cima
                if cp[cc] < 30*Nf:
                    cp[cc] = cp[cc] + 1
            else:
                print('erro: estado fora da faixa')
#
        if entre_floor == 0: # carro em um floor
            if cm[cc] == 0: # carro bloqueado - fora de serviço
                cm[cc] = 0
            elif cm[cc] == 1: # parado durante viagem para baixo
                ct[cc] = ct[cc] + 1
                if ct[cc] > 5:
                    if fb[floor][0] == True: # embarca para baixo
                        cont1 = 0
                        lim = len(fq[floor])
                        dest = []
                        while cont1 < lim:
                            if fq[floor][cont1][4] < floor:
                                dest = dest + [fq[floor][cont1][4]]
                                cb[cc][fq[floor][cont1][4]] = True
                                cL[cc].append(fq[floor].pop(cont1))
                                lim = len(fq[floor])
                            else:
                                cont1 = cont1 + 1
                        fb[floor][0] = False
                        if cd[cc] > np.min(dest):
                            cd[cc]= np.min(dest)
                    if cd[cc] == floor:
                        cm[cc] = 3
                    else:
                        if cp[cc] > 0:
                            cp[cc] = cp[cc] - 1
                            cm[cc] = 4
            elif cm[cc] == 2: # parado durante viagem para cima
                ct[cc] = ct[cc] + 1
                if ct[cc] > 5:
                    if fb[floor][1] == True: # embarca para cima
                        cont1 = 0
                        lim = len(fq[floor])
                        dest = []
                        while cont1 < lim:
                            if fq[floor][cont1][4] > floor:
                                dest = dest + [fq[floor][cont1][4]]
                                cb[cc][fq[floor][cont1][4]] = True
                                cL[cc].append(fq[floor].pop(cont1))
                                lim = len(fq[floor])
                            else:
                                cont1 = cont1 + 1           
                        fb[floor][1] = False
                        if cd[cc] < np.max(dest):
                            cd[cc]= np.max(dest)
                    if cd[cc] == floor:
                        cm[cc] = 3
                    else:
                        if cp[cc] < 30*Nf:
                            cp[cc] = cp[cc] + 1
                            cm[cc] = 5
            elif cm[cc] == 3: # parado ocioso - sem missão atribuída
                cm[cc] = 3
            elif cm[cc] == 4: # viajando para baixo
                if cb[cc][floor] == True or fb[floor][0] == True or\
                   cd[cc] == floor:
                    cm[cc], ct[cc] = 1, 0
                    if cb[cc][floor] == True: # desembarca
                        cont1=0
                        lim = len(cL[cc])
                        while cont1 < lim:
                            if cL[cc][cont1][4] == floor:
                                cL[cc][cont1][2] = ts
                                Listp.append(cL[cc].pop(cont1))
                                lim = len(cL[cc])
                            else:
                                cont1 = cont1 + 1
                        cb[cc][floor] == False
                else:
                    if cp[cc] > 0:
                        cp[cc] = cp[cc] - 1
                    else: cm[cc] = 3
            elif cm[cc] == 5: # viajando para cima
                if cb[cc][floor] == True or fb[floor][1] == True or\
                   cd[cc] == floor:
                    cm[cc], ct[cc] = 2, 0
                    if cb[cc][floor] == True: # desembarca
                        cont1=0
                        lim = len(cL[cc])
                        while cont1 < lim:
                            if cL[cc][cont1][4] == floor:
                                cL[cc][cont1][2] = ts
                                Listp.append(cL[cc].pop(cont1))
                                lim = len(cL[cc])
                            else:
                                cont1 = cont1 + 1
                        cb[cc][floor] == False
                else:
                    if cp[cc] < 30*Nf:
                        cp[cc] = cp[cc] + 1
                    else: cm[cc] = 3
            else:
                print('erro: estado fora da faixa')
    
##
tempos_de_viagem = np.zeros(len(Listp))
for i in range(len(Listp)):
    tempos_de_viagem[i] = Listp[i][2] - Listp[i][1]
av_viagem = np.sum(tempos_de_viagem)/len(Listp)
print(av_viagem)
##
ne = 0
for i in range(Nf):
    ne = ne + len(fq[i])
print(ne)
for i in range(Nc):
    ne = ne + len(cL[i])
print(ne)
ne = ne + len(Listp)
print(ent_id, ne)

















