
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import Button, HoverTool, ColumnDataSource, \
                        CategoricalColorMapper, LinearColorMapper,  \
                        TapTool, BoxSelectTool, BoxZoomTool, ResetTool, PanTool,\
                         CustomJS
from bokeh.models import Select
from bokeh.palettes import plasma
from bokeh.transform import transform
from bokeh.layouts import column, layout
from bokeh.io import curdoc




def get_notebook_bokeh_fields():
    '''
    Returns the important bokeh functions needed for easy notebook use

    Returns
    show : bokeh show structure
        use by taking the output of a scatter plot interactive funting
        and passing it into show: `show(p)`
    output_notebook : bokeh function to render plots in notebook
        use by running in a cell as follows: `output_notebook()`

    '''
    return show, output_notebook

def scatter_plot_interactive(x, y, labels, colors=None, 
                 multi_color_names=None,
                 title=None, x_label=None, y_label=None, 
                 plot_size=(600, 600), 
                 use_color_mapper=True, show_color_mouseover=False):
    '''
    A 2D bokeh scatter plot with colors and labels so you can mouse over
    to see the label info.
    
    Parameters
    ----------
    x : list of floats/ints
        x positions
    y : list of floats/ints
        y positions
    labels : list of strings
        Any textual info you want to be associated with each scatter plot point
    colors : list of floats/ints or list of lists of floats/ints
        If `multi_color_names` is `None` (no input provided) the colors must be a list
        of floats or ints. 
        If `multi_color_names` is not none, then colors must be a list of the 
        same length as multi_color_names, and contain lists of floats/ints (of the same
        length as x and y)
    multi_color_names : `None` or list of strings : optional
        If No input provided, or None, then this does nothing.
        But if it is not none, it must be a list of strings. 
        This triggers a special js function which will add a selection box above 
        the plot.
        The selection box is a dropdown menu with elements, the memebers of which
        are the strings/elements of this list.
    title : str : optional
        The title provided to the plot
    x_label : str : optional
        The label for the x axis
    y_label : str : optional
        the label for the y axis
    plot_size : tuple of ints : optional
        Passing a tuple of two ints will determine the size of the plot.
        The default is `(600, 600)` which coorsponds to width and heigth respectively.
    use_color_mapper : bool : optional
        A boolean to indicate whether or not to remap the provided colors 
        (Not currently functional)
    show_color_mouseover : bool : optional
        A boolean, if true the color value will be displayed next to the point 
        when the point is moused over
    Returns
    -------
    p : bokeh plot object
        The plot that has been built from the input fields.
        Will need to be passed into `show` to display
    Notes
    -----
    This function is still in development and needs to break more often and 
    more specifically. But hopefully it still makes it easy to bring in basic
    yet informative scatter plots into notebooks for data exploration. 
    '''
    def handle_color(c, use_color_mapper):
        '''
        Be able to automap colors using mapper, or
        take given rgb values 
        (or maybe allow matplotlib color api as well?)
        '''
        c = [float(x) for x in c]
        if type(c[0]) == int or type(c[0]) == float and use_color_mapper:
            #print("MAPPED")
            mapper = LinearColorMapper(palette=plasma(256), low=min(c), high=max(c))
        return mapper
    def normalize_colors(c):
        '''
        map every float in colors(a list of colors) to a 0-1 range
        '''
        print(min(c), max(c))
        if min(c) == max(c):
            return [0 for x in c]
        nc = [(i - min(c))/(max(c)-min(c)) for i in c]
        return nc
        
    
    # # Check if plot size is defined

    assert type(plot_size) == tuple
    assert len(plot_size) == 2
    assert type(plot_size[0]) == int
    assert type(plot_size[1]) == int
    #     defined_size = True
    #     # TODO: Add error info
    # else:
    #     plot_size = (600,600)
        
    
    # Handle color options
    if not isinstance(multi_color_names, type(None)):
        # Test assertions
        # . . .
        # Assign colors
        color_d = {}
        for i in range(len(multi_color_names)):
            colors[i] = normalize_colors(colors[i])
            c = colors[i]
            cname = multi_color_names[i]
            color_d[cname] = c#transform('colors', handle_color(c, use_color_mapper))
            
        select = Select(title="Coloring:", value=multi_color_names[0], options=multi_color_names)
        #select.js
        data=dict(x=x, y=y, labels=labels, color=colors[multi_color_names.index(select.value)])
        for key in color_d:
            data['c_'+key] = color_d[key]#transform(color_d[key], handle_color(color_d[key], use_color_mapper))
        source = ColumnDataSource(data)
        #source.data['multi_color_namess']  = color_d

        
    else:
            
        colors = [float(x) for x in colors]
        if type(colors[0]) == int or type(colors[0]) == float and use_color_mapper:
            #print("MAPPED")
            mapper = LinearColorMapper(palette=plasma(256), low=min(colors), high=max(colors))
        #print(type(colors[0]))
        
        source = ColumnDataSource(data=dict(x=x, y=y, labels=labels, color=colors))
        
    tooltips=[
        ("index", "$index"),
        ("(x,y)", "(@x, @y)"),
        ('labels', '@labels'),
    ]
    if show_color_mouseover:
        tooltips.append(('color', '@color'))
    hover = HoverTool(tooltips=tooltips)
    #print(hover)
    
    
    p = figure(plot_width=plot_size[0], plot_height=plot_size[1], 
               tools=[hover, TapTool(), BoxSelectTool(), BoxZoomTool(), ResetTool(), PanTool()], 
               title=title, x_axis_label = x_label, y_axis_label=y_label
              )



    callback = CustomJS(args=dict(source=source, p=p), code="""
            var data = source.data;
            var f = cb_obj.value;
            var color = data['c_'+f];
            data['color'] = color;
            source.change.emit();
            p.change.emit();
            
        """)

    #select.on_change(p.circle('x', 'y', size=10,source=source))
    if not isinstance(multi_color_names, type(None)):
        #print(select.value)
        #print(color_d[select.value])
        select.js_on_change('value', callback)
            
        c = transform('color',handle_color(color_d[select.value], use_color_mapper))
        p.circle('x', 'y', size=10, source=source,
                 fill_color=c)
        layout = column(select, p)
        return layout
    else:    
        #p.add_tools(HoverTool(tooltips=hover), TapTool(), BoxSelectTool(), BoxZoomTool(), ResetTool(), PanTool())
        p.circle('x', 'y', size=10, source=source,
                 fill_color=transform('color', mapper))
        return p