################################################## IMPORT / VARIABILI #####################################################

from cv2 import cv2
from PIL import Image
from gooey import Gooey, GooeyParser
from matplotlib import pyplot as plt
import argparse
import time
import numpy as np
import os
import sys
import shutil
import json
import logging
import glob
import ntpath


# -- conversione delle immagini da CR2 a JPG (necessaria per l'elaborazione successiva)
def conversion(inputPath, outputPath):
    processing = 1
    outputFilename = []
    print(' ')
    print('Conversione immagini in corso...')
    # -- conversione CR2 to JPG
    for directory, subdirectories, files in os.walk(inputPath):
        for file in files:
            if(file.endswith('.CR2')):
                print('Conversione: ',processing,'/',(len(glob.glob(inputPath+"/*.CR2")+glob.glob(inputPath+"/*/*.CR2")+glob.glob(inputPath+"/*/*/*.CR2"))))
                size = len(file)
                direct = directory
                parent = os.path.dirname(direct)
                new_set = direct.replace(parent, '')
                im = Image.open(os.path.join(directory,file))
                if not os.path.exists(outputPath+new_set):
                    os.makedirs(outputPath+new_set, exist_ok=True)
                rgb_im = im.convert('RGB')
                rgb_im.save(outputPath+'/temp/'+file[:size-4]+'.jpg')
                output = outputPath+new_set+'/'+file[:size-4]+'.jpg'
                processing += 1
                outputFilename.append(output)
    print('Immagini convertite con successo!')
    print(' ')
    # -- lista di tutti gli output corretti
    return outputFilename


# -- export in formato TIFF
def tiffExport(inputPath, outputPath, outputFilename):
    processing = 1
    print('Esportazione immagini in corso...')
    for directory, subdirectories, files in os.walk(inputPath):
        for file in files:
            print('Esportazione: ',processing,'/',len(files))
            if(file.endswith('.jpg')):
                size = len(file)
                im = Image.open(inputPath+'/'+file)
                for output in outputFilename:
                    parent = os.path.dirname(output)
                    if not os.path.exists(parent):
                        os.makedirs(parent, exist_ok=True)
                    if(file == ntpath.basename(output)):
                        im.save(parent+'/'+file[:size-4]+'.tif', 'TIFF')
            processing += 1
    print('Immagini esportate in formato TIFF con successo!')
    print(' ')


# -- algoritmo per il bilanciamento del bianco (Greyworld)
def white_balance(img):
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result


# -- processamento immagine, riconoscimento e ritaglio
def cropping(inputPath, outputPath, l_padding, t_padding, r_padding, b_padding, imgQuality, application, imgViewer, outputFilename):
    processing = 1
    print('Processamento immagini in corso...')
    # -- ciclo che processa tutti i file nella cartella delle immagini convertite
    for directory, subdirectories, files in os.walk(outputPath+'/temp'):
        for file in files:
            path = outputPath+'/temp/'+file
            # -- stampa file in fase di ritaglio
            print('Processamento: ',processing,'/',len(files))
            #print('Directory: ' + directory)
            print(' | Immagine: ' + file, end='\r')
            processing += 1

            img = cv2.imread(path)
            # -- conversione scala di colori
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # -- applicazione dilatazione bordi (migliore identificazione oggetto)
            kernel = np.ones((31, 31), np.uint8)
            dil = cv2.dilate(gray, kernel, iterations=1)
            # -- applicazione threshold
            _, th = cv2.threshold(dil, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # -- identificazione contorni e area maggiore (quella dell'oggetto in questione)
            _, contours, _= cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            areas = [cv2.contourArea(c) for c in contours]
            max_index = np.argmax(areas)
            cnt=contours[max_index]
            # -- assegnazione e stampa parametri ritaglio
            x,y,w,h = cv2.boundingRect(cnt)

            # -- crea uno switch per attivare o meno l'inversione pixels (si in caso di fondo chiaro, no in caso di fondo scuro)
            # -- se le coordinate rilevate sono sostanzialmente errate attiva l'inversione e ripeti il processo (da ottimizzare TBD)
            if(x<500):
                th_er1 = cv2.bitwise_not(th)
                _, contours, _= cv2.findContours(th_er1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                areas = [cv2.contourArea(c) for c in contours]
                max_index = np.argmax(areas)
                cnt=contours[max_index]
                x,y,w,h = cv2.boundingRect(cnt)

            # -- ottenimento parametri immagine
            height, width, channel = img.shape  

            # -- applicazione padding
            # -- in alcuni casi il padding rilevato coincide con il bordo dell'immagine e applicare i parametri sotto da' risultato nullo
            x -= l_padding
            if(x < 0):
                x = 0
            y -= t_padding
            if(y < 0):
                y = 0
            w += r_padding + int(l_padding)
            if(w > width):
                w = width
            h += b_padding + int(t_padding)
            if(h > height):
                h = height
            # -- file ritagliato
            cropped_image = img[y:y+h, x:x+w]
            
            img_rect = img.copy()
            # -- disegno contorni identificati su immagine viewer
            cv2.rectangle(img_rect,(x,y),(x+w,y+h),(0,255,0),13)

            # -- viewer fasi processo
            if(imgViewer == True):
                plt.figure()
                plt.subplot(131), plt.imshow(img_rect)
                plt.title("Individuata")
                plt.subplot(132), plt.imshow(th)
                plt.title("Threshold")
                plt.subplot(133), plt.imshow(cropped_image)
                plt.title("Risultato")
                plt.show()

            height, width, channel = cropped_image.shape
            # -- rotazione immagine in base all'applicazione
            cropped_image = imgRotation(width, height, file, cropped_image, application)
            
            # -- applicazione bilanciamento del bianco
            balanced_image = white_balance(cropped_image)

            # -- salvataggio immagine ritagliata e JSON con metadati
            jsonExport(outputPath, width, height, file, imgQuality, outputFilename) 
            cv2.imwrite(os.path.join(outputPath+'/cropped', file), balanced_image)
    print('Immagini processate con successo!')


# -- rotazione immagine in base al nome file
def imgRotation(width, height, file, cropped_image, application):
    subL = "Left"
    subR = "Right"
    if(application == 'V-Scanner'):
        if(width>height):
            if(subL in file):
                # -- 'Left' ruotati di 90 gradi a sinistra
                cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif(subR in file):
                # -- 'Right' ruotati di 90 gradi a destra
                cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
            else:
                cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
    # -- Piano aspirato ruota sempre di 90 gradi a destra
    elif(application == 'Piano aspirato'):
        cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_CLOCKWISE)
    # -- altrimenti non ruotare
    return cropped_image


# -- esportazione JSON contenente metadati immagine
def jsonExport(outputPath, width, height, file, imgQuality, outputFilename):
    size = len(file)
    data = {
                'info' : [
                    {
                        'file': file
                    },
                    {
                        'width' : width,
                        'height' : height
                    },
                    {
                        'quality' : imgQuality
                    },
                ],
            }      
    json_object = json.dumps(data, indent = 4)       
    for output in outputFilename:
        parent = os.path.dirname(output)
        if not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        if(file == ntpath.basename(output)):
             with open(parent+'/'+file[:size-4]+'.json', 'w') as outfile:
                outfile.write(json_object)


# -- controllo dell'integrità dei file (controllo file vuoti, da sistemare)
def integrityCheck(inputPath, outputPath, l_padding, t_padding, r_padding, b_padding):
    print(' ')
    print('Controllo integrità file...')
    processing = 0
    # -- controllo integrità immagini
    for directory, subdirectories, files in os.walk(outputPath+'/cropped'):
        for file in files:
            filePath = outputPath+'/cropped/'
            if(os.path.getsize(filePath+file) == 0): 
                processing += 1
    print('Controllo completato! Immagini corrotte o danneggiate: ',processing)


# -- applicazione profilo colore
def cpApplication(inputPath, outputPath, cpPath, forceProcessing, exportFormat):
    if(not cpPath == False):
        print(' ')
        print('Applicazione profilo colore...')
        # -- applicazione profilo colore
        # -- '-o' = output; '-p' = color profile; '-Y' = force processing (sovrascrivi); '-c' = input
        if(forceProcessing == True):
            os.system('rawtherapee-cli -o '+outputPath+'/jpg_export -p '+cpPath+' -Y -c '+outputPath+'/cropped')
        else:
            os.system('rawtherapee-cli -o '+outputPath+'/jpg_export -p '+cpPath+' -c '+outputPath+'/cropped')

        print('Profilo colore applicato con successo!')
        print(' ')
    else:
        print(' ') 
        print('Profilo colore non applicato!')
        print(' ')


# -- compressione immagini JPG
def compressImg(outputPath, imgQuality):
    processing = 1
    print('Compressione immagini in corso...')
    try:
        for directory, subdirectories, files in os.walk(outputPath+'/jpg_export'):
            for file in files:
                if(file.endswith('.jpg')):
                    print('Compressione: ',processing,'/',int(len(files)))
                    img = Image.open(outputPath+'/jpg_export/'+file)
                    img.save(outputPath+'/jpg_export/'+file, optimize=True, quality=int(imgQuality))
                    processing += 1
        print('Compressione effettuata con successo!')
    except IOError as e:
        print("Errore: %s - %s." % (e.filename, e.strerror))


# -- reinserimento in copia cartelle di origine
def reFolder(inputPath, outputPath, outputFilename, cpPath):
    print(' ')
    print('Risistemazione JPG nelle cartelle...')
    if(cpPath == True):
        for directory, subdirectories, files in os.walk(outputPath+'/jpg_export'):
            for file in files:
                for output in outputFilename:
                    parent = os.path.dirname(output)
                    if not os.path.exists(parent):
                        os.makedirs(parent, exist_ok=True)
                    if(file == ntpath.basename(output)):
                        shutil.move(outputPath+'/jpg_export/'+file, parent)
    else:
        for directory, subdirectories, files in os.walk(outputPath+'/cropped'):
            for file in files:
                for output in outputFilename:
                    parent = os.path.dirname(output)
                    if not os.path.exists(parent):
                        os.makedirs(parent, exist_ok=True)
                    if(file == ntpath.basename(output)):
                        shutil.move(outputPath+'/cropped/'+file, parent)
    print('Spostamento effettuato con successo!')


# -- inizializzazione Gooey
@Gooey(
    program_name='pyCrop',       # Defaults to script name
    default_size=(750, 800),   # starting size of the GUI
    menu=[{
        'name': 'File',
        'items': [{
                'type': 'AboutDialog',
                'menuTitle': 'Info',
                'name': 'pyCrop',
                'description': 'Applicazione per il processamento automatico di immagini',
                'version': '1.0.0',
                'copyright': '2022',
                'developer': 'Federico Dassiè',
                'license': 'MIT'
            }]
        },{
        'name': 'Aiuto',
        'items': [{
                'type': 'MessageDialog',
                'menuTitle': 'Guida all\'utilizzo',
                'caption': 'Guida all\'utilizzo',
                'message': '1) Per iniziare scegli l\'applicazione da utilizzare: Piano aspirato (rotazione 90 gradi), V-Scanner (le pagine dei libri si aggiusteranno in modo corretto in base al loro prefisso del nome file, "Left" e "Right") o Other (nessuna rotazione). \n\n2) Inserisci il percorso di input, da dove prendere le immagini da processare, poi il percorso di output nello spazio sottostante, dove vuoi salvare i risultati. \n\n3) Seleziona il formato di esportazione delle immagini, il quale potrà essere JPG e/o TIFF in base alle esigenze. Per quanto riguarda il formato JPG è disponibile una compressione immagine nella barra sottostante, in modo da poter ridurre le dimensioni sul disco delle immagini. \n\n4) Oltre a ciò, nei parametri facoltativi, esiste la possibilità di inserire un profilo colore (se hai un file .pp3 da applicare) ed effettuare un taglio personalizzato alle immagini, aggiungendo o rimuovendo spazio (inserendo valori positivi o negativi) nella direzione desiderata. \n\nUna sezione di debug, che permette all\'utente di controllare la funzionalità e l\'identificazione immagine durante la fase di processo, è disponibile sul fondo dell\'applicazione.'
            }]
    }],
    image_dir='/home/swarchive/Scrivania/federico/pyCrop/icons',
    required_cols=1,           # number of columns in the "Required" section
    optional_cols=2,           # number of columns in the "Optional" section
    clear_before_run=True,
    show_stop_warning=True,
    show_failure_modal=True,
    hide_progress_msg=True,
    dump_build_config=False,   # Dump the JSON Gooey uses to configure itself
    load_build_config=None,    # Loads a JSON Gooey-generated configuration
    monospace_display=False,   # Uses a mono-spaced font in the output screen
    #navigation="TABBED",
    )   
def main():
    # -- path cartelle di input e output da assegnare poi da Terminale
    inputPath = '' 
    outputPath = ''
    # -- color profile path (.pp3) da assegnare poi da Terminale
    cpPath = ''
    # -- padding immagine da assegnare poi da Terminale (h = horizontal; v = vertical)
    t_padding = ''
    b_padding = ''
    l_padding = ''
    r_padding = ''
    # -- forceProcessing sovrascrive dati già presenti con lo stesso nome
    forceProcessing = True
    # -- formato di esportazione
    exportFormat = ''
    # -- parametro qualità immagini
    imgQuality = 0
    # -- variabile per il conteggio degli elementi processati in ogni ciclo
    processing = 1
    # -- nomi file originali jpg
    outputFilename = []

    # -- file log
    logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
    logger=logging.getLogger(__name__)

    # -- dimensioni image viewer
    plt.rcParams["figure.figsize"] = (12,8)


    ################################################## GESTIONE INPUT UTENTE ##################################################

    apps = ['Piano aspirato', 'V-Scanner', 'Other (nessuna rotazione richiesta)']
    choice = ['yes','no']

    parser = GooeyParser(description='Postproduzione automatica delle immagini')
    subs = parser.add_subparsers(help="commands", dest="command")
    
    # -- Required parameters section
    fprocessing = subs.add_parser(
        "file_processing", prog="File processing",
    ).add_argument_group("Parametri obbligatori")

    fprocessing.add_argument(
        "Applicazione",
        metavar="Applicazione",
        help="Seleziona la funzionalità che vuoi usare",
        widget="Listbox",
        choices=apps
    )

    fprocessing.add_argument(
        "Percorso di input",
        metavar="Percorso di input",
        help="Cartella da cui verranno prese le immagini da processare",
        widget="DirChooser",
        gooey_options=dict(
            wildcard="Cartella di input", full_width=True,
        ),
    )

    fprocessing.add_argument(
        "Percorso di output",
        metavar="Percorso di output",
        help="Cartella in cui verranno salvati i risultati",
        widget="DirChooser",
        gooey_options=dict(
            wildcard="Cartella di output", full_width=True,
        ),
    )

    fprocessing.add_argument(
        "--jpgformat", 
        dest='Formato JPG',
        help="Esporta in formato JPG", 
        action="store_true",
        default=True
    )

    fprocessing.add_argument(
        "--tifformat",
        dest='Formato TIFF',
        help="Esporta in formato TIFF",
        action="store_true"
    )

    fprocessing.add_argument(
        '--imgquality', 
        action="store", 
        default=50, 
        dest='Qualità immagine', 
        widget='Slider', 
        help='Compressione immagine (0-100)'
    )

    # -- Optional parameters section
    optional=fprocessing.add_argument_group('Parametri facoltativi')

    optional.add_argument(
        '--fp', 
        action="store", 
        widget='Dropdown', 
        choices=choice, 
        default='yes', 
        dest='Forza processo', 
        help='Sovrascrizione file'
    )

    optional.add_argument(
        '--colorProfile', 
        action="store", 
        dest='File profilo colore', 
        widget='FileChooser', 
        #default='/home/swarchive/Scrivania/federico/pyCrop/profiles/DEFAULT.pp3',
        help='Seleziona il profilo colore in formato .pp3', 
        gooey_options=dict(
            wildcard="File profilo colore (*.pp3)|*.pp3"
        )
    )

    optional.add_argument(
        '--tpadding', 
        action="store", 
        default=0, 
        dest='Padding sopra (px)', 
        help='Spazio extra/rimosso sopra l\'immagine', 
        type=int
    )

    optional.add_argument(
        '--bpadding', 
        action="store", 
        default=0, 
        dest='Padding sotto (px)', 
        help='Spazio extra/rimosso sotto l\'immagine', 
        type=int
    )

    optional.add_argument(
        '--lpadding', 
        action="store", 
        default=0, 
        dest='Padding sinistra (px)', 
        help='Spazio extra/rimosso a sinistra dell\'immagine', 
        type=int
    )

    optional.add_argument(
        '--rpadding', 
        action="store", 
        default=0, 
        dest='Padding destra (px)', 
        help='Spazio extra/rimosso a destra dell\'immagine', 
        type=int
    )

    # -- Debug section
    debug=optional.add_argument_group('Debug')
    debug.add_argument(
        "--showres", 
        dest='Mostra progressione',
        help="Abilita il visualizzatore per ogni immagine processata (nota: questo rallenterà il processo e le finestre dovranno essere chiuse manualmente)", 
        action="store_true",
        default=False
    )
    
    args = vars(parser.parse_args())
    inputPath = args['Percorso di input']
    outputPath = args['Percorso di output']
    forceProcessing = args['Forza processo']
    cpPath = args['File profilo colore']
    if(args['Formato JPG']):
        exportFormat = '.jpg'
    if(args['Formato TIFF']):
        exportFormat = '.tif'
    imgQuality = args['Qualità immagine']
    imgViewer = args['Mostra progressione']
    
    
    print('▄▄▄▄▄ Controllo input: ▄▄▄▄▄')
    if args['Applicazione']:
        application = args['Applicazione']
        print('▄ Applicazione: ', args['Applicazione'])
    else:
        application = 'Piano aspirato'
        print('▄ Applicazione: non inserita, utilizzo di default "Piano aspirato"')

    if args['Percorso di input']:
        if(not(os.path.exists(args['Percorso di input']))):
            print('▄ Percorso di input non esistente, per favore riprova')
        else:
            print('▄ Percorso di input: ',args['Percorso di input'])

    if args['Percorso di output']:
        if(not(os.path.exists(args['Percorso di output']))):
            print('▄ Percorso di output non esistente, per favore riprova')
        else: 
            print('▄ Percorso di output: ',args['Percorso di output'])

    if args['Forza processo']:
        if(forceProcessing == 'yes'):
            forceProcessing == True
            print('▄ Forza processo: YES')
        elif(forceProcessing == 'no'):
            forceProcessing == False
            print('▄ Forza processo: NO')
        else:
            print('▄ Opzione di sovrascrizione non valida')
            print(' ')
    else:
        forceProcessing == False

    print('▄ Qualità immagine: ',args['Qualità immagine'])

    if args['Formato JPG'] and args['Formato TIFF']:
        print('▄ Esportazione in: JPG and TIFF')
    elif args['Formato JPG']:
        print('▄ Esportazione in: JPG')
    elif args['Formato TIFF']:
        print('▄ Esportazione in: TIFF')

    if args['File profilo colore']:
        if(os.path.exists(args['File profilo colore'])):
            print('▄ Profilo colore: ',args['File profilo colore'])
        else:
            print('▄ Percorso profilo colore non esistente, non verrà applicato')
            cpPath = False
    else: 
        print('▄ Percorso profilo colore non esistente, non verrà applicato')
        cpPath = False

    try:
        t_padding = int(args['Padding sopra (px)'])
        print('▄ Padding sopra: ',args['Padding sopra (px)'],'px')
    except:
        t_padding = 0
        print('▄ Padding sopra: 0 px')

    try:
        b_padding = int(args['Padding sotto (px)'])
        print('▄ Padding sotto: ',args['Padding sotto (px)'],'px')
    except:
        b_padding = 0
        print('▄ Padding sotto: 0 px')

    try:
        l_padding = int(args['Padding sinistra (px)'])
        print('▄ Padding sinistra: ',args['Padding sinistra (px)'],'px')
    except:
        l_padding = 0
        print('▄ Padding sinistra: 0 px')

    try:
        r_padding = int(args['Padding destra (px)'])
        print('▄ Padding destra: ',args['Padding destra (px)'],'px')
    except:
        r_padding = 0
        print('▄ Padding destra: 0 px')
    
    print(' ')


    ######################################################### ESECUZIONE #####################################################

    try:      
        # -- inizializzazione
        start_time = time.time()
        
        # -- creazione cartelle temporanee
        if not os.path.exists(outputPath+'/cropped'): 
            os.makedirs('/'+outputPath+'/cropped',exist_ok=True)
        if not os.path.exists(outputPath+'/temp'): 
            os.makedirs('/'+outputPath+'/temp',exist_ok=True)
        if(args['Formato TIFF'] == True):
            if not os.path.exists(outputPath+'/tiff_export'): 
                os.makedirs('/'+outputPath+'/tiff_export',exist_ok=True)
        if(args['Formato JPG'] == True):
            if not os.path.exists(outputPath+'/jpg_export'): 
                os.makedirs('/'+outputPath+'/jpg_export',exist_ok=True)
        
        # -- esecuzione
        outputFilename = conversion(inputPath, outputPath)
        cropping(inputPath, outputPath, l_padding, t_padding, r_padding, b_padding, imgQuality, application, imgViewer, outputFilename)
        integrityCheck(inputPath, outputPath, l_padding, t_padding, r_padding, b_padding)

        shutil.rmtree(outputPath+'/temp')
        cpApplication(inputPath, outputPath, cpPath, forceProcessing, exportFormat)
        
        
        if(args['Formato TIFF'] == True):
            if(cpPath == True):
                inputP = outputPath+'/jpg_export'
            else: 
                inputP = outputPath+'/cropped'
            outputP = outputPath+'/tiff_export'
            tiffExport(inputP, outputP, outputFilename)

        #if(args['Formato JPG'] == True):
        #    src = outputPath+'/cropped'
        #    dest = outputPath+'/jpg_export'
        #    file_names = os.listdir(src)
        #    for file_name in file_names:
        #       shutil.move(os.path.join(src, file_name), dest)
        compressImg(outputPath, imgQuality)
        
        reFolder(inputPath, outputPath, outputFilename, cpPath)

        # -- messaggio di fine output
        print('Immagini processate con successo!')
    except EnvironmentError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
        logger.error(e)


    ##################################################### OPERAZIONI FINALI ###################################################

    # -- cancella cartelle temporanee
    try:
        shutil.rmtree(outputPath+'/cropped')
        #if(args['Formato JPG'] == False or len(os.listdir(outputPath+'/jpg_export')) == 0):
        shutil.rmtree(outputPath+'/jpg_export')
        #if(args['Formato TIFF'] == False or len(os.listdir(outputPath+'/tiff_export')) == 0):
        shutil.rmtree(outputPath+'/tiff_export')
    except OSError as e:
        print("Errore: %s - %s." % (e.filename, e.strerror))
        logger.error(e)

    # -- apertura automatica cartella di output a fine esecuzione
    #if(exportFormat == '.tif'):
    os.system('xdg-open "%s"' % outputPath)
    #else:
    #    if(cpPath == False):
    #        os.system('xdg-open "%s"' % outputPath+'/cropped')
    #    else: 
    #        os.system('xdg-open "%s"' % outputPath+'/jpg_export')
    print(' ')

    # -- stampa durata processo
    time_elapsed = (time.time() - start_time)
    mins = time_elapsed/60
    hs = time_elapsed/3600

    if(time_elapsed < 60):
        print('Durata processo: '+str(time_elapsed)[0:4]+' secondi')
    elif(time_elapsed > 60 and time_elapsed < 3600):
        print('Durata processo: '+str(mins)[0:4]+' minuti')
    elif(time_elapsed > 3600):
        print('Durata processo: '+str(hs)[0:4]+' ore')

    print(' ')


# -- esecuzione
main()