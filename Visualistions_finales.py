from matplotlib.pyplot import text
import pandas as pd
from bokeh.models import HoverTool, CustomJS, DateRangeSlider, Div, Paragraph, Dropdown, Select
from bokeh.palettes import Set1
from datetime import date
from bokeh.layouts import row, column 
from bokeh.plotting import figure, show, ColumnDataSource,output_file
import numpy as np
from bokeh.palettes import Category10, Category20
from bokeh.transform import cumsum
from bokeh.tile_providers import get_provider, Vendors
import json


# EN TETE ----------------------------------------------------------------------------------------------------------

div_image = Div(text="""
                <img src="Ports.png" />
                """, width=1200, height=200)
div_entete = Div(
                 text = """
<h1 style="color:white;">VISUALISATIONS DE DONNEES SUR LES PORTS DE LA REGION BRETAGNE</h1>
"""
                 
                 , width=1500, height=100)
par_entete=Div(text="""<p>Cette page a pour objectif de présenter les ports appartenant à la région Bretagne à travers différents graphiques 
               et cartes. Les différentes visualisations ont pour objectifs de donner quelques repères géographiques, économiques et logistiques sur une selection
               de ports de la région Bretagne. Ces derniers sont de véritables aujourd'hui de véritables acteurs du développement touristiques, économique ou encore culturel de la région. 
               </p><hr style="width:1500px">""", height=50)




# PREMIERE VISUALISATION  -----------------------------------------------------------------------------------

def coor_wgs84_to_web_mercator(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x,y)

#Import des données
fp = open("ports-appartenant-a-la-region-bretagne.geojson","r",encoding='utf-8')
dico = json.load(fp)

#Création du dictionnaire
commune=[]
nom_du_port = []
coordx = []
coordy= []
ls_activites = []#Contient sous formes de listes les différentes activités du port en question

for p in dico["features"]:
    commune.append(p["properties"]["commune"])
    nom_du_port.append(p["properties"]["nom"])
    X,Y = coor_wgs84_to_web_mercator(p["geometry"]["coordinates"][0],p["geometry"]["coordinates"][1])
    coordx.append(X)
    coordy.append(Y)
    ls = []
    if(p["properties"]["reparation_navale"]==1):
        ls.append(" réparation navale")
    if(p["properties"]["commerce"]==1):
        ls.append(" commerce")
    if(p["properties"]["peche"]==1):
        ls.append(" pêche")
    if(p["properties"]["plaisance"]==1):
        ls.append(" plaisance")
    ls_activites.append(ls)

#Création du dataframe et de la source
df2 = pd.DataFrame({'commune': commune, 'nom_du_port':nom_du_port, 'coordx': coordx, 'coordy':coordy, "ls_activites":ls_activites})
source = ColumnDataSource(df2)

#Création de la carte
p2 = figure(margin=(10,0,10,0),width=1100,height=600,x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom", title="Ports appartenant à la région Bretagne",  tools="pan,wheel_zoom,box_zoom,reset")
tile_provider = get_provider(Vendors.CARTODBPOSITRON)
p2.add_tile(tile_provider)

#Création des éléments graphiques représentant les ports
p2.circle_x(x="coordx",y="coordy",source =source,size =15, fill_color = "white", alpha=1,  
           line_color ="navy")
p2.circle_cross(x="coordx",y="coordy",source =source,size =10, fill_color = "white", fill_alpha=0.5,  
           line_color ="navy")

#Création de quelques éléments graphiques
hover_tool = HoverTool(tooltips=[( 'Commune', '@commune'),( 'Nom du port', '@nom_du_port'),('Activités', '@ls_activites')])
p2.xaxis.ticker = []
p2.yaxis.ticker = []
p2.add_tools(hover_tool)
p2.xgrid.grid_line_color = None
p2.ygrid.grid_line_color = None
p2.outline_line_width = 3
p2.outline_line_alpha = 1
p2.outline_line_color = "navy"
p2.toolbar.logo = None

#texte
par2 = Div(text="""
           <p>Voici la carte de l'ensemble des ports de la région Bretagne.
                 La Bretagne en possède 22. Pour chaque port, vous trouverez le nom du port,
                 de la commune ainsi que les activités portuaires.</p>""",margin=(100,0,0,30))
                
div2 = Div(text="""
<a href="https://data.bretagne.bzh/explore/dataset/ports-appartenant-a-la-region-bretagne/table/?location=8,48.12577,-2.91138&basemap=jawg.streets ">Lien vers la base de données</a>""",margin=(10,0,0,30))

# DEUXIEME GRAPHIQUE --------------------------------------------------------------------------------------

#traitement préalable des données
df1 = pd.read_csv("trafic-marchandises-ports.csv", sep = ";")

df_trafic = df1[["Date", "Nom du port", "Trafic total (en tonnes)"]]
df_trafic.Date = pd.to_datetime(df_trafic.Date)


df_trafic.columns = ['Date', 'Nom', 'Trafic']
df_trafic.Trafic = df_trafic.Trafic/1000

df_brest = df_trafic[df_trafic.Nom  == 'BREST'].sort_values(by = 'Date')
df_lorient = df_trafic[df_trafic.Nom  == 'LORIENT'].sort_values(by = 'Date')
df_roscoff = df_trafic[df_trafic.Nom  == 'ROSCOFF'].sort_values(by = 'Date')
df_legue = df_trafic[df_trafic.Nom  == 'LE LÉGUÉ'].sort_values(by = 'Date')
df_malo = df_trafic[df_trafic.Nom  == 'SAINT-MALO'].sort_values(by = 'Date')

df_brest = ColumnDataSource(df_brest)
df_lorient = ColumnDataSource(df_lorient)
df_roscoff = ColumnDataSource(df_roscoff)
df_legue = ColumnDataSource(df_legue)
df_malo = ColumnDataSource(df_malo)

#graphique
p1 = figure(margin=(10,0,10,0),title = "Trafic de marchandises des ports de la région Bretagne",
            x_axis_type = "datetime", x_axis_label = "Date", 
            y_axis_label = "Trafci total (en milliers de tonnes)", width = 1000,
            tools = ['save', 'box_zoom'], y_range = (-10,400))
p1.toolbar.logo = None

palette = Set1[5]

p1.line(x = 'Date', y = 'Trafic', source = df_brest, legend_label = 'Brest', color = palette[0])
p1.line(x = 'Date', y = 'Trafic', source = df_lorient,legend_label = 'Lorient', color = palette[1])
p1.line(x = 'Date', y = 'Trafic', source = df_roscoff,legend_label = 'Roscoff', color = palette[2])
p1.line(x = 'Date', y = 'Trafic', source = df_legue,legend_label = 'Le Légué', color = palette[3])
p1.line(x = 'Date', y = 'Trafic', source = df_malo, legend_label = 'Saint-Malo', color = palette[4])

p1.legend.location = "top_left"
p1.legend.click_policy = "hide"

#affichage de la valeur au survol
hover_tool = HoverTool(tooltips=[( 'Date','@Date{%F} '),
                                 ('Trafic', '@Trafic')],
                        formatters={'@Date' : 'datetime'})
p1.add_tools(hover_tool)


##selection des dates pour l'axe des abscisses
date_range_slider = DateRangeSlider(title="Sélectionnez la date souhaitée",
                                    value=(date(2016, 3, 1), date(2020, 8, 1)),
                                    start=date(2016, 3, 1), end=date(2020, 8, 1),margin=(10,90,0,30))
date_range_slider.js_on_change("value", CustomJS(code="""
    console.log('date_range_slider: value=' + this.value, this.toString())
"""))

date_range_slider.js_link("value", p1.x_range, "start", attr_selector=0)
date_range_slider.js_link("value", p1.x_range, "end", attr_selector=1)


#texte
par1 = Paragraph(text="""Voici l'évolution du trafic mensuel de marchandises 
                (en milliers de tonnes) entre le 1er mars 2016 et le 1er août 2020 pour les
                ports de commerce appartenant à la région Bretagne.Vous ouvez sélectionner le
                port souhaité et les différentes valeurs de trafic sur le graphique""",margin=(100,30,0,30))
                
div1 = Div(text="""
<a href="https://data.bretagne.bzh/explore/dataset/trafic-marchandises-des-ports-de-la-region-bretagne/table/?dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJsaW5lIiwiZnVuYyI6IkNPTlNUQU5UIiwieUF4aXMiOiJ0cmFmaWNfdG90YWxfZW5fdG9ubmVzIiwic2NpZW50aWZpY0Rpc3BsYXkiOnRydWUsImNvbG9yIjoicmFuZ2UtRGFyazIifV0sInhBeGlzIjoiZGF0ZSIsIm1heHBvaW50cyI6IiIsInRpbWVzY2FsZSI6Im1vbnRoIiwic29ydCI6IiIsInNlcmllc0JyZWFrZG93biI6Im5vbV9kdV9wb3J0IiwiY29uZmlnIjp7ImRhdGFzZXQiOiJ0cmFmaWMtbWFyY2hhbmRpc2VzLWRlcy1wb3J0cy1kZS1sYS1yZWdpb24tYnJldGFnbmUiLCJvcHRpb25zIjp7fX19XSwiZGlzcGxheUxlZ2VuZCI6dHJ1ZSwiYWxpZ25Nb250aCI6dHJ1ZX0%3D ">Lien vers la base de données</a>""",margin=(10,0,0,30))


# TROISIEME VISUALISATION -----------------------------------------------------------------------------------

#Import des données
#df = pandas.read_csv('espaces-de-concessions-des-ports-et-aeroports-appartenant-a-la-region-bretagne.csv', 
#                     encoding = 'utf-8', sep=';')
dft = pd.read_csv('ports-appartenant-a-la-region-bretagne.csv', encoding='utf-8', sep=';')

#DataFrame des sites
#Série des villes
df_ville = dft.loc[:,"commune"]
df_ville = pd.Series(df_ville)

#Séries de la somme des concessions par ville
df3 = dft.loc[:,['plaisance','peche','commerce','reparation_navale','passager']]
df_somme = df3.sum(axis=1)
df_somme = pd.Series(df_somme)

#Dataframe pour faire la somme des concessions sur une même ville
df_test = pd.concat([df_ville,df_somme],axis=1)
grouped = df_test.groupby(['commune'])
df_fin = grouped.agg('sum')

#Initialisation des index
df_fin.reset_index(level=0, inplace=True)

#Transformtion en Séries
df_ville = pd.Series(df_fin['commune'])
df_somme = pd.Series(df_fin[0])

#Dataframe complet sur les sites
dict_sites = {df_ville[i]: df_somme[i] for i in range(len(df_ville))}
df_sites = pd.Series(dict_sites).reset_index(name='valeur').rename(columns={'index':'type'})
df_sites['angle'] = df_sites['valeur']/df_sites['valeur'].sum()*2*np.pi
df_sites['color'] = Category20[len(dict_sites)] 


#DataFrame des concessions
#Série des concessions
df_conces = ["Plaisance", "Peche", "Commerce", "Reparation navale", "Passager"]
df_conces = pd.Series(df_conces)

#Série de la somme des concessins
df_somme = [dft["plaisance"].sum(),dft["peche"].sum(),dft["commerce"].sum(),dft["reparation_navale"].sum(),dft["passager"].sum()]
df_somme = pd.Series(df_somme)

#Dataframe complet sur les concessions
dict_concession = {df_conces[i]: df_somme[i] for i in range(len(df_conces))} 
df_concession = pd.Series(dict_concession).reset_index(name='valeur').rename(columns={'index':'type'})
df_concession['angle'] = df_concession['valeur']/df_concession['valeur'].sum()*2*np.pi
df_concession['color'] = Category10[len(dict_concession)]


#Dictionnaire des données
don_pie_chart = {
    'Concession': dict(type=list(df_concession['type']),
               valeur=list(df_concession['valeur']),
               angle=list(df_concession['angle']),
               color=list(df_concession['color'])),
    'Site': dict(type=list(df_sites['type']),
               valeur=list(df_sites['valeur']),
               angle=list(df_sites['angle']),
               color=list(df_sites['color']))
    }

#Différents titres
titres = {
    'Concession': "Nombre des différents types de concessions en bretagne",
    'Site': "Nombres de concessions suivant le site maritime"    
    }


#Définition du ColumnDataSource, initialisé sur les concessions
source_pie_chart = ColumnDataSource(don_pie_chart['Concession'])

#Création de la figure
pie_chart = figure(margin=(10,0,10,0),title="Nombre de ports par concession en bretagne", width = 900, height = 700
                , tools = ['save'])
pie_chart.toolbar.logo = None
pie_chart.wedge(x=0, y=1, radius=0.7, source=source_pie_chart, fill_color='color', legend_field='type',
                line_color="white", start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'))

#Création de l'outil de survol
hover_pie_chart = HoverTool(tooltips=[('Type ', '@type'),('Nombre', '@valeur')])
pie_chart.add_tools(hover_pie_chart)

#Arrière plan du graphique
pie_chart.axis.axis_label=None
pie_chart.axis.visible=False
pie_chart.grid.grid_line_color = None

#Paramètres de la légende
pie_chart.legend.location = 'top_left'
pie_chart.legend.background_fill_color = 'lightgray'
pie_chart.legend.background_fill_alpha = 0.7


#Callback 
callback = CustomJS(args = {'source': source_pie_chart, 'data': don_pie_chart,
                            'title': pie_chart.title, 'titres': titres},
                    code = """source.data = data[cb_obj.value] 
                             title.text = titres[cb_obj.value]
                         """)

#Selection de la figure
select = Select(title = 'Choisissez ce que vous voulez afficher :', 
                value = 'Concession', options = ['Concession', 'Site'] ,margin=(10,0,0,30))
select.js_on_change('value', callback)

#texte
par3 = Paragraph(text="""Diagramme cicurlaire représentant les différentes cocnessions des principaux
                 ports de la région Bretagne, à savoir les ports de Brest, Lorient
                 et Saint-Malo. Vous pouvez visualiser sur le diagramme le type de concession
                 et le nombre de ports associé.""",margin=(100,0,0,30))
                
div3 = Div(text="""
<a href="https://data.bretagne.bzh/explore/dataset/espaces-de-concessions-des-ports-et-aeroports-appartenant-a-la-region-bretagne/information/ ">Lien vers la base de données</a>""",margin=(10,0,0,30))



# QUATRIEME VISUALISATION : CARTE DES CONCESSIONS ET ZONES PORTUAIRE ------------------------------------------------------------------------------

#Import des données
fp2 = open("espaces-de-concessions-des-ports-et-aeroports-appartenant-a-la-region-bretagne.geojson","r",encoding='utf-8')
dico2 = json.load(fp2)

#Construction du dictionnaire
site=[]
concession = []
coordx = []# les coordonnées x et y serviront à construire un multiplygone. Ils seront donc de la forme "[[[]]]"
coordy= []

for p in dico2["features"]:
    site.append(p["properties"]["site"])
    concession.append(p["properties"]["concession"])
    xc=[]
    yc=[]
    if(p["geometry"]):
        for c in p["geometry"]["coordinates"][0][0]:
            X,Y=coor_wgs84_to_web_mercator(c[0], c[1])
            xc.append(X)
            yc.append(Y)
    coordx.append([[xc]])
    coordy.append([[yc]])

#Construction du dataframe
df = pd.DataFrame({'site': site, 'concession':concession, 'coordx': coordx, 'coordy':coordy})
df_port = df[df['concession']!='AEROPORT']#On ne garde que les ports
source = ColumnDataSource(df_port)
source1 = ColumnDataSource(df_port)

#Creation de la carte
p4 = figure(margin=(10,0,10,0),width=1100,height=600,x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom", title="Zones portuaires et concessions de la région Bretagne",  tools="pan,wheel_zoom,box_zoom,reset")
tile_provider = get_provider(Vendors.CARTODBPOSITRON)
p4.add_tile(tile_provider)
print(df_port)
#Création des multipolygones pour les zones
p4.multi_polygons('coordx', 'coordy', source=source1,color = 'navy', fill_color='navy',
                     fill_alpha = 0.3)
hover_tool = HoverTool(tooltips=[('Site', '@site'),('Concessions', '@concession')])
p4.add_tools(hover_tool)

#Creation de l'outil de choix des ports 
#On récupère la liste des ports et on créer le menu
ls=list(source.data['site'])
ls=list(set(ls))
menu = Dropdown(label='Choisissez un port', menu=ls,margin=(10,30,0,30))

#On créé un curtomJS pour changer les coordonnées des polygones suivant le choix du port
callback=CustomJS(args=dict(source=source1,ts=source), code="""
                    var data=ts.data;
                    var site=data['site'];

                    var concession=data['concession'];
                    var coordx=data['coordx'];
                    var coordy=data['coordy'];

                    var data1=source.data;
                    var f=cb_obj.item;

                    var s=[];
                    var c=[];
                    var x=[];
                    var y=[];

                    for(var i=0;i<concession.length; i++){
                        if(site[i]==f){
                          x.push(coordx[i]);
                          y.push(coordy[i]);
                          c.push(concession[i]);
                          s.push(site[i]);

                        }
                    }
                    data1['coordx']=x;
                    data1['coordy']=y;
                    data1['site']=s;
                    data1['concession']=c;

                    source.change.emit();
            """)


menu.js_on_event('menu_item_click', callback)

# Quelques éléments graphiques
p4.xaxis.ticker = []
p4.yaxis.ticker = []
p4.xgrid.grid_line_color = None
p4.ygrid.grid_line_color = None
p4.outline_line_width = 3
p4.outline_line_alpha = 1
p4.outline_line_color = "navy"
p4.toolbar.logo = None

#texte
par4 = Paragraph(text="""Carte représentant les différentes zones portuaires associées au choix du port. Pour chaque zone, vous trouverez le nom du site et la concession associée. (parfois nécéssaire de rafraîchir le graphique pour afficher correctement)""",margin=(100,30,0,30))


# PIED DE PAGE

div_pp = Div(text="""
             <h3> Page réalisée dans le cadre d'un projet de visualisation python sur Bokeh.</h3>    
             <h3> Auteurs : Guillaume Béguec - Ewen Le Cunff - Maël Mandard</h3>           
             """)

#affichage
layout = column(div_image,div_entete,par_entete,row(p2,column(par2, div2)), Div(text="""<hr style="width:1500px">"""),
                row( column(par1, date_range_slider, div1),p1),Div(text="""<hr style="width:1500px">"""),
                row(pie_chart, column(par3,select , div3)), Div(text="""<hr style="width:1500px">"""),
                row(column(par4, menu), p4),Div(text="""<hr style="width:1500px">"""),div_pp)
output_file(filename=("index.html"))

show(layout)