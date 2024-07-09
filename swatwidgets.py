from parameterdb import rch_components,sub_components
import bqplot.pyplot as plt
import numpy as np
import ipyleaflet
from ipywidgets import widgets, Layout
from ipyleaflet import WidgetControl,FullScreenControl,GeoJSON,Map,LayersControl
import json
import random
from outputservice import  *
from observationdb import observations
from parameterdb import filetypes,parameters
from ipywidgets import *
from modelservice import ModelService
from branca.colormap import linear
from pyecharts.charts import Line,Grid
from outputservice import process_rch_file,process_sub_file,collect_simulations
from observationdb import observations,permap
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from hydroeval import evaluator, nse,kge,kgeprime,rmse,kgenp,mare,pbias
from IPython.display import display

        
def InspectorWidget(longtitude:float,latitude:float,filelist:list):
    def createToolBar():
        def on_value_change(change):
            if change['new']=="Reach":
                w4.options=rch_components
            else:
                w4.options=sub_components
            w4.value=w4.options[0]
        
        
        def addToList(b):
            if w1.value!="" and w1.value!=None:
                tvalue=w1.value
                temp_list = list(w1.options)
                temp_list.remove(tvalue)
                w1.options=temp_list
                temp_list = list(w2.options)
                temp_list.append(tvalue)
                w2.options=temp_list
                w2.value=tvalue
        def removeFromList(b):
            if w2.value!="" and w2.value!=None:
                tvalue=w2.value
                temp_list = list(w2.options)
                temp_list.remove(tvalue)
                w2.options=temp_list
                temp_list = list(w1.options)
                temp_list.append(tvalue)
                w1.options=temp_list
                w1.value=tvalue
        
        addbutton = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            icon='arrow-down', # (FontAwesome names without the `fa-` prefix)
            layout={'width':'40px','height':'24px'}
        )
        
        addbutton.on_click(addToList)
        removebutton = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            layout={'width':'40px','height':'24px'},
            icon='arrow-up'
        )
        removebutton.on_click(removeFromList)
        simulations=list(collect_simulations("./model/"))
        box_layout = Layout(display='flex', align_items='center' )
        box2=widgets.VBox(children=[addbutton,removebutton])
        outterbox=widgets.HBox(layout=box_layout)
        label=widgets.Label("Simulations:")
        w1=widgets.Dropdown()
        if simulations!=None and len(simulations[1:])>0:
            w1.options=simulations[1:]
            w1.value=simulations[1]
        w2=widgets.Dropdown()
        if simulations!=None and len(simulations[:1])>0:
            w2.options=simulations[:1]
            w2.value=simulations[0]
        w1.layout.width='100px'
        w2.layout.width='100px'
        label2=widgets.Label("Source:")
        w3=widgets.Dropdown(options=['Reach','Subbasin'],value='Reach')
        w3.layout.width='100px'
        w3.observe(on_value_change, names='value')
        w4=widgets.Dropdown(options=rch_components)
        w4.value=w4.options[0]
        w4.layout.width='100px'
        box1=widgets.VBox(children=[w1,w2])
        box3=widgets.VBox(children=[w3,w4])
        label3=widgets.Label("Include Observation:")
        box_layout = Layout(display='flex', align_items='center' )
        observed=widgets.ToggleButtons(
        options=['Yes', 'No'],
        value='No',
        style={'button_width':'60px'},
        disabled=False,
        button_style='info', # 'success', 'info', 'warning', 'danger' or ''
        #icons=['check-square','minus-square'] 
        )
        
        box4=VBox(children=[label3,observed],layout=box_layout)

        outterbox.children=[label,box1,box2,label2,box3,box4]
        return outterbox,w2,w3,w4,observed

    def random_color(feature):
        return {
            'color': 'black',
            'fillColor': random.choice(['red', 'yellow', 'green', 'orange']),
        }
    
    def clickFeature(event, feature,properties):
        tfig=createFigure(properties["Subbasin"])
        chartbox.widget=tfig
        m.add(chartbox)     
            
    def createFigure(subbasin:int):
        # Sample data
        fig = plt.figure(layout=dict(height="200px", width="400px"),fig_margin=fig_margin,legend_style={'width':'40px','stroke': 'none'},legend_text={'font-size': 8},legend_location='top-left')
        #marks=generate_makerstrs()
        x_data=get_timeseries("./model/file.cio")
        y_datas=[]
        obs_labels=[]
        for file in selectedSimulations.options:
            file_path = './model/'
            file_path=file_path+file+".output."
            obs=None
            if selectedDataSource.value=="Reach":
                file_path=file_path+"rch"
                df = process_rch_file(file_path)
                if includedObs.value=="Yes":
                    try:
                        obs=observations["reach.xls"][str(subbasin)][selectedVariable.value].values
                    except KeyError:
                        obs=None
            else:
                file_path=file_path+"sub"
                df = process_sub_file(file_path)
                if includedObs.value=="Yes":
                    try:
                        obs=observations["subbasin.xls"][str(subbasin)][selectedVariable.value].values
                    except KeyError:
                        obs=None
            df=df.loc[(subbasin,),selectedVariable.value]
            y_data = df.values
            y_datas.append(y_data)
            if isinstance(obs,np.ndarray):
                y_datas.append(obs)
                obs_labels.append("obs_"+selectedVariable.value)   
        line = plt.plot(x_data, y_datas,labels=selectedSimulations.options+tuple(obs_labels),display_legend=True,axes_options={'x':{'num_ticks':6}}) 
        plt.ylabel(selectedVariable.value)       
        return fig

    def closeChartBox(event,type,coordinates):
        if type=="preclick":
            try:
                m.remove_control(chartbox)
            except Exception as e:
                #print(e)
                pass
            
    def on_play_change(change):
        new_dt64 = firstday + np.timedelta64(change["new"], 'D')
        cdt_str = new_dt64.astype(str)
        dayLabel.value= cdt_str.split('T')[0]
        if selectedDataSource.value=="Reach":
            dayLabel.value= "Please select a variable that are associated with a subbasin!"
            return
        for item in m.layers:
            if item not in layers:
                m.remove(item)

        
        choro_data=get_choro_data(variable=selectedVariable.value,step=change["new"],simulation=selectedSimulations.value)
        layer2 = ipyleaflet.Choropleth(
        name="Choropleth",
        geo_data=geo_json_data,
        choro_data=choro_data,
        key_on='oid',
        colormap=linear.YlOrRd_04,
        border_color='black',
        style={'fillOpacity': 1, 'dashArray': '5, 5'})
        m.add(layer2)
    # Create the base map
    m = Map(center=[latitude, longtitude], zoom=11, basemap=ipyleaflet.basemaps.OpenStreetMap.Mapnik)
    style={'opacity': 1, 'dashArray': '9', 'fillOpacity': 0.1, 'weight': 1}
    river_style={'color':'blue','opacity': 1, 'dashArray': '0', 'fillOpacity': 0.1, 'weight': 2}
    hover_style={'color': 'white', 'dashArray': '0', 'fillOpacity': 0.5 }
    
    f=open(r"./data/subbasins.json","r")
    geo_json_data=json.load(f)
    f.close()
    
    for filename in filelist:   
        f=open(r"./data/"+filename+".json","r")
        data=json.load(f)
        f.close()
        if filename=='rivers':
            fstyle=river_style
        else:
            fstyle=style
        geo_json = GeoJSON(
        name=filename,
        data=data,
        style=fstyle,
        hover_style=hover_style 
        )
        if filename=='subbasins':
            geo_json.on_click(clickFeature)
        m.add(geo_json)

    fig_margin = dict(top=10, bottom=30, left=50, right=30) 
    fig = plt.figure(layout=dict(height="200px", width="400px"),fig_margin=fig_margin,legend_style={'width':'40px'},legend_location="top-left",legend_text={'font-size': 8})
    chartbox = WidgetControl(widget=fig, position='bottomright',max_width=400)
    toolbar,selectedSimulations,selectedDataSource,selectedVariable,includedObs=createToolBar()
    toolbox=WidgetControl(widget=toolbar, position='topright')
    m.add(toolbox)
    m.add(FullScreenControl())
    m.on_interaction(closeChartBox)
    firstday=get_timeseries("./model/file.cio")[0]
    dt_str = firstday.astype(str)
    date_part = dt_str.split('T')[0]
    layers=m.layers
    play=Play(min=1,
    max=len(get_timeseries("./model/file.cio")),    
    value=1,
    step=1,
    interval=500,
    description="Press play",
    disabled=False)
    play.observe(on_play_change, names='value')
    dayLabel=Label(value=date_part)
    playbar=HBox(children=[play,dayLabel])
    playbox=WidgetControl(widget=playbar, position='bottomleft')  
    #print(linear.YlOrRd_04._repr_html_() )
    with open('colormap.svg', 'r') as file:
        html_content = file.read()
    colormapbox=WidgetControl(widget=HTML(value=html_content), position='bottomleft',transparent_bg=True)   
    m.add(colormapbox)
    m.add(playbox)
    layercontrol = LayersControl(position='topright')
    m.add(layercontrol)
    mapcontainer=widgets.HBox(children=[m])
    mapcontainer.layout.height='400px'
    return mapcontainer

def ModelWidget():
    simulationName=Text(
        value='Simulation1',
        placeholder='Type Simulation Name',
        description='SimName:'
    )

    output=Output(description="b",layout=Layout(width='98%', height='280px'))

    def create_and_append_widget(widget_type, description, **kwargs):
        style = {'description_width': 'initial'}
        widget = widget_type(description=description, **kwargs)
        LevelTwoVBox1.children = tuple(list(LevelTwoVBox1.children)[:-1] + [widget]+[list(LevelTwoVBox1.children)[-1]])

    def add_widget_on_click(b):
        for item in LevelTwoVBox1.children:
            if isinstance(item,FloatSlider) and item.description==parameterSelecter.label+"."+fileSelecter.label:
                return
        create_and_append_widget(FloatSlider, description=parameterSelecter.label+"."+fileSelecter.label, 
                                min=parameterSelecter.value[0], max=parameterSelecter.value[1])

    @output.capture()
    def execution_widget_on_click(b):
        output.clear_output()
        global simulationCount
        print("this procedure is executed");
        paramerterEdit=ModelService()
        hasAtLeastOneParameter=False;
        for item in LevelTwoVBox1.children:
            if isinstance(item,FloatSlider):
                hasAtLeastOneParameter=True
                paramerterEdit.addCalibrationParameter("v__"+item.description, str(item.value))
        if hasAtLeastOneParameter:
            paramerterEdit.saveToModelIn("./model/")
            paramerterEdit.invokeModel("./model/",simulationName.value)

    addParaButton = Button(description="Add Parameter")
    addParaButton.on_click(add_widget_on_click)

    fileSelecter=Dropdown(
        options=filetypes,
        description='File:'
    )

    parameterSelecter=Dropdown(
        options=parameters["gw"],
        description='Parameter:'
    )

    def on_value_change(change):
        parameterSelecter.options=parameters[change.new]


    fileSelecter.observe(on_value_change, names='value')


    LevelOneHBox=widgets.GridBox(layout=widgets.Layout(grid_template_columns='40% 60%'))
    LevelTwoVBox1 = VBox()
    LevelTwoVBox2 = VBox()
    LevelThreeHBox=HBox()
    executeButton = Button(description="Execute")
    executeButton.on_click(execution_widget_on_click)
    LevelThreeHBox.children=[addParaButton,executeButton]
    LevelTwoVBox1.children = [simulationName,fileSelecter,parameterSelecter,LevelThreeHBox]
    LevelTwoVBox2.children=[output]
    LevelOneHBox.children=[LevelTwoVBox1,LevelTwoVBox2]
    return LevelOneHBox


def PerformanceWidget():   
        def r_squared(obs, sim):
            residuals = obs - sim
            ss_res = np.sum(residuals ** 2)
            ss_tot = np.sum((obs - np.mean(obs)) ** 2)
            r2 = 1 - (ss_res / ss_tot)
            return r2
        
        def calculatePerformance(sim,obs):
            values=[]
            for item in w4.options: 
                if item=="Nash-Sutcliffe Efficiency":
                    key="NSE"
                    value= evaluator(nse, sim, obs, axis=0)
                    value=value[0]
                elif item=="Original Kling-Gupta Efficiency":
                    key="KGE"
                    value=  evaluator(kge, sim, obs, axis=0)
                    value=value[0]
                elif item=="Modified Kling-Gupta Efficiency":  
                    key="kgeprime"  
                    value=  evaluator(kgeprime, sim, obs, axis=0)
                    value=value[0]
                elif item=="Non-Parametric Kling-Gupta Efficiency":
                    key="kgenp"
                    value=  evaluator(kgenp, sim, obs, axis=0)
                    value=value[0]
                elif item=="Root Mean Square Error":
                    key="RMSE"
                    value=  evaluator(rmse, sim, obs, axis=0)
                    value=value[0]
                elif item=="Mean Absolute Relative Error":
                    key="MARE"
                    value=  evaluator(mare, sim, obs, axis=0)
                    value=value[0]
                elif item=="Percent Bias":
                    key="pbias"
                    value=  evaluator(pbias, sim, obs, axis=0)
                    value=value[0]
                elif item=="Coefficient of Determination":
                    key="R2"
                    value=   r_squared(obs, sim)
                values.append((key,value))
            return values
    
    
        def recreateChart(change):
            #simulations=collect_simulations('./model/')
            simulations=w2.options
            performanceset=[]
            for outputtype, subs in observations.items():
                for sub,df in subs.items():
                    for col in df.columns:
                        obs= df[col]
                        for s in simulations:
                            file_path = './model/'
                            file_path=file_path+s+".output."
                            if outputtype=="reach.xls":
                                file_path=file_path+"rch"  
                                dataset=process_rch_file(file_path)
                                sim=dataset.loc[(int(sub),),col]
                                fu="rch"
                            else:
                                file_path=file_path+"sub"  
                                dataset=process_sub_file(file_path)
                                sim=dataset.loc[(int(sub),),col]
                                fu="sub"
                            nse_value = calculatePerformance(sim, obs)
                            #print(nse_value)
                            pa=[list((s,fu,sub,col, *item)) for item in nse_value]
                            performanceset.append(pa)
                            #print(pa)
            ##print(performanceset)
            if len(performanceset)>0:
                combinelist=performanceset[0]
                for i in range(1,len(performanceset)):
                    combinelist=combinelist+performanceset[i]
            #print(combinelist)
            df=pd.DataFrame(combinelist,columns=("sim","oty","fun","var","ind","val"))
            #print(df)
            
            g=df.groupby(["oty","fun","var"])
            tab_contents=[]
            tab_children=[]
            for key,item in g.groups.items():
                title=("_".join(key)).upper()
                tab_contents.append(title)
                c=Output()
                tab_children.append(c)
                subdf=g.get_group(key)
                line = Line()
                x=list(simulations)
                line.add_xaxis(x)
                inx=0
                for v in w4.options:
                    y=subdf.loc[subdf["sim"].isin(simulations)].loc[subdf["ind"]==permap[v]]["val"]
                    y=list(y.to_numpy())
                    line.add_yaxis(v, list(y),yaxis_index=inx)
                    inx=inx+1
                    
                for i in range(1,len(w4.options)):
                    line.extend_axis(
                        yaxis=opts.AxisOpts(
                            name=permap[w4.options[i]],
                            name_location="end",
                            position="right",
                            is_show=True,
                            offset=50*(i-1),
                            axisline_opts=opts.AxisLineOpts(is_show = True),
                            splitline_opts=opts.SplitLineOpts(is_show=False) ,
                            axistick_opts=opts.AxisTickOpts(is_show=True)
                        )
                    )
                
                line.set_global_opts(
                    xaxis_opts=opts.AxisOpts(
                        axisline_opts=opts.AxisLineOpts(is_on_zero= False)
                    ),
                    yaxis_opts=opts.AxisOpts(
                        name=permap[w4.options[0]],
                        name_location="end"                                                                                                       
                    ),
                    toolbox_opts=opts.ToolboxOpts(
                        pos_bottom="10%",
                        pos_left="10%",
                        feature=opts.ToolBoxFeatureOpts(
                            magic_type=  opts.ToolBoxFeatureMagicTypeOpts( is_show = False),
                            brush=None
                            #save_as_image = opts.ToolBoxFeatureSaveAsImageOpts(),
                            #restore = opts.ToolBoxFeatureRestoreOpts(),
                            #data_view = opts.ToolBoxFeatureDataViewOpts(),
                            #data_zoom = opts.ToolBoxFeatureDataZoomOpts()       
                        )
                    )
                )
                
                line.set_series_opts(
                    label_opts=opts.LabelOpts(
                        is_show=True,
                        position="top",
                        formatter=JsCode("function(params){return params.value[1].toString().substring(0,6);}")
                    )
                )

                grid = Grid()
                postright=str((len(w4.options)-1)*5)+"%"
                grid.add(line, opts.GridOpts(pos_left="5%",pos_bottom="5%", pos_right=postright), is_control_axis_index=True)                   
                with c:
                    rs=grid.render_notebook()
                    display(rs)
            
            tab = widgets.Tab()
            tab.children= tab_children
            tab.titles = tab_contents
            chart_box.children=[tab]
        
        def moveAll1(b):
            w1.options=list(w2.options)+list(w1.options)
            w2.options=[]
            w2.value=[]
        
        def addAll1(b):
            w2.options=list(w2.options)+list(w1.options)
            w1.options=[]
            w1.value=[]
            
        def add1(b):
            w2.options=list(w2.options)+list(w1.value)
            tlist=[item for item in w1.options if item not in w1.value]
            w1.options=tlist
            
            
        def move1(b):
            w1.options=list(w1.options)+list(w2.value)
            tlist=[item for item in w2.options if item not in w2.value]
            w2.options=tlist 
            
        def moveAll2(b):                                                      
            w3.options=list(w4.options)+list(w3.options)               
            w4.options=[]                                              
            w4.value=[]                                                
                                                                
        def addAll2(b):                                                
            w4.options=list(w4.options)+list(w3.options)               
            w3.options=[]                                              
            w3.value=[]      

        def add2(b):                                                   
            w4.options=list(w4.options)+list(w3.value)                 
            tlist=[item for item in w3.options if item not in w3.value]
            w3.options=tlist   
            
        def move2(b):                                                  
            w3.options=list(w3.options)+list(w4.value)                 
            tlist=[item for item in w4.options if item not in w4.value]
            w4.options=tlist                                            
        
        b1 = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            icon='angle-double-right', # (FontAwesome names without the `fa-` prefix)
            layout={'width':'40px','height':'24px'}
        )
        b1.on_click(addAll1)
        
        b2 = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            layout={'width':'40px','height':'24px'},
            icon='angle-right'
        )
        b2.on_click(add1)
        
        b3 = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            icon='angle-left', # (FontAwesome names without the `fa-` prefix)
            layout={'width':'40px','height':'24px'}
        )
        b3.on_click(move1)
        
        b4 = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            layout={'width':'40px','height':'24px'},
            icon='angle-double-left'
        )
        b4.on_click(moveAll1)
        
        simulations=list(collect_simulations("./model/"))
        box_layout = Layout(display='flex', align_items='center' )
        box1=widgets.VBox(children=[b1,b2,b3,b4])
        
        label1=widgets.Label("Simulations:")
        w1=widgets.SelectMultiple(rows=6)
        if simulations!=None and len(simulations[1:])>0:
            w1.options=simulations[1:]
            w1.values=simulations[1]
        w2=widgets.SelectMultiple(rows=6)
        if simulations!=None and len(simulations[:1])>0:
            w2.options=simulations[:1]
            w2.values=simulations[0]
        w1.layout.width='100px'
        w2.layout.width='100px'
        
        b5 = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            icon='angle-double-right', # (FontAwesome names without the `fa-` prefix)
            layout={'width':'40px','height':'24px'}
        )
        b5.on_click(addAll2)

        b6 = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            layout={'width':'40px','height':'24px'},
            icon='angle-right'
        )
        b6.on_click(add2)
        
        b7 = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            icon='angle-left', # (FontAwesome names without the `fa-` prefix)
            layout={'width':'40px','height':'24px'}
        )
        b7.on_click(move2)
        
        b8 = widgets.Button(
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            layout={'width':'40px','height':'24px'},
            icon='angle-double-left'
        )
        b8.on_click(moveAll2)

        simulations=list(collect_simulations("./model/"))
        box2=widgets.VBox(children=[b5,b6,b7,b8])
        label2=widgets.Label("Indices:")
        w3=widgets.SelectMultiple(rows=6)
        w3.options=["Nash-Sutcliffe Efficiency","Original Kling-Gupta Efficiency","Modified Kling-Gupta Efficiency","Non-Parametric Kling-Gupta Efficiency","Root Mean Square Error","Mean Absolute Relative Error","Percent Bias"]    
        w4=widgets.SelectMultiple(rows=6)
        w4.options=["Coefficient of Determination"]
        w3.layout.width='220px'
        w4.layout.width='220px'          
        editor_box=HBox(children=[label1,w1,box1,w2,label2,w3,box2,w4],layout=box_layout)
        chart_box=HBox()
        w2.observe(recreateChart,"options")
        w4.observe(recreateChart,"options")
        recreateChart("init")       
        container_box=VBox(children=[editor_box,chart_box])
        return container_box
        
if __name__ == "__main__":
    longtitude=118.01177670289091
    latitude=25.440411737132468
    filelist=["rivers","outlets","subbasins"]
    InspectorWidget(longtitude,latitude,filelist)