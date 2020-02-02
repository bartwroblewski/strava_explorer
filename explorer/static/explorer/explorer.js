class Model {
    constructor() {}
    
    bindDataChanged(callback) {
        this.onDataChanged = callback
    }
    
    async getData(params) {
        let url = new URL(explorer_data_absurl) // url is defined in the template
        url.search = new URLSearchParams(params)
        let response = await fetch(url)
        let json = await response.json()
        this.onDataChanged(json)
        //return json
    }    
    
}

class View {
    constructor() {
        this.wait_message                = this.getElement('#wait_message')
        
        // heatmap
        this.heatmap_container           = this.getElement('#heatmap_container')
        this.heatmap                     = this.getElement('#heatmap')
        this.heatmap_x_select            = this.getElement('#heatmap_x_select')
        this.heatmap_y_select            = this.getElement('#heatmap_y_select')   
        this.heatmap_z_select            = this.getElement('#heatmap_z_select')   
        this.heatmap_color_select        = this.getElement('#heatmap_color_select')
        this.heatmap_reversescale_button = this.getElement('#heatmap_reversescale_button')
        this.reversescale                = false // value changes on button click
        this.heatmap_x_value             = '' // clicked x
        this.heatmap_y_value             = '' // clicked y
        
        // map
        this.map_layer_select            = this.getElement('#map_layer_select') 
        this.map_toggle                  = this.getElement('#map_toggle')
        this.polyline_tooltip            = this.getElement('#polyline_tooltip')
        this.remembered_opacity          = 0 // temp for reverting back to polyline's original opacity on mouseout
        this.mouse_x                     = 0
        this.mouse_y                     = 0
        this.trackMouse()
        //this.map_container               = this.getElement('#map_container')
        //this.map                         = this.getElement('#map')
        
        this.initial                     = true // checks if to add heatmap click listener
 
    }
    
    allowSelectOptions(allowed_options) {
        let selects = [this.heatmap_z_select, this.map_layer_select]
        selects.forEach(select => {
            Array.from(select.options).forEach(option => {
                if (!allowed_options.includes(option.value)) {
                    option.disabled = true
                }
            })
        })
    }
    
    bindHeatmapAxisChanged(handler) {
        this.heatmap_container.addEventListener('click', e => {
            if (e.target.parentElement.className === 'heatmap_axis_select') {
                this.heatmap_x_value = '' // reset clicked x
                this.heatmap_y_value = '' // reset clicked y
                this.inputs[e.target.className] = e.target.value
                handler()
            }
        })      
    }
    
    bindHeatmapColorChanged(handler) {
        this.heatmap_color_select.addEventListener('change', e => {
            handler()
        })
        this.heatmap_reversescale_button.addEventListener('click', e => {
            this.reversescale = !this.reversescale
            handler()
        })
    }
    
    bindMapLayerChanged(handler) {
        this.map_layer_select.addEventListener('change', e => {
            handler()
        })
        
    }
    
    bindMapToggleChanged(handler) {
        this.map_toggle.addEventListener('change', e => {
            handler()
        })  
    }
    
    get inputs() {
        // Inputs to be sent as request params
        let heatmap_x_name = this.heatmap_x_select.value
        let heatmap_y_name = this.heatmap_y_select.value
        let heatmap_z_name = this.heatmap_z_select.value
        let map_layer      = this.map_layer_select.value
        let inputs = {
            'heatmap_x_name': heatmap_x_name,
            'heatmap_y_name': heatmap_y_name,
            'heatmap_z_name': heatmap_z_name,
            'map_layer'     : map_layer, 
        }
        inputs[heatmap_x_name] = this.heatmap_x_value // e.g 'year': 2019'
        inputs[heatmap_y_name] = this.heatmap_y_value
        console.log('INPUTS', inputs)
        return inputs
    }
    
    getElement(selector) {
        let element = document.querySelector(selector)
        return element
    }
    
    createElement(tag, class_name) {
        let element = document.createElement(tag)
        if (class_name) document.className = class_name
        return element
    }
    
    trackMouse() {
    // track mouse moves to display
    // polylines tooltips in correct places     
        
        let self = this
        
        window.addEventListener('mousemove', function(e) {       
            self.mouse_x = e.clientX
            self.mouse_y = e.clientY
        })
    }
    
    createHeatmap(data, heatmap_click_callback) {
        console.log('DATA PASSED TO CREATE HEATMAP:', data)
        let heatmap_data = [{
            x: data.x_axis,
            y: data.y_axis,
            z: data.z_axis,
            type: 'heatmap',
            colorscale: this.heatmap_color_select.value,
            reversescale: this.reversescale,
            xgap: .5,
            ygap: .5,
        }]
        let layout = {
            title: 'Activities heatmap (click cells to filter)',
            font: {
                family: 'BebasNeueRegular',
            },
            //autosize: true,
            //width: 650,
            //height: 400,
            //plot_bgcolor: 'silver',
            xaxis: {
                title: { 
                    text: `${this.heatmap_x_select.selectedOptions[0].textContent}`,
                },
                tickformat: 'd',
            },
            yaxis: {
                title: {
                    text: `${this.heatmap_y_select.selectedOptions[0].textContent}`,
                },
            },      
            margin: {
                // l: 60,
                //~ r: 10,
               // b: 60,
             //   t: 40, 
            }
        }
        
        try {
            Plotly.react(this.heatmap.id, heatmap_data, layout)
        } catch(e) {
            alert('Something went wrond with heatmap axis scaling. Please make sure your window is maximized and there is no browser console open, then reload the page.')
        }
        
        // only attach listener on first heatmap creation
        if (this.initial) {
            console.log('initial true')
            this.initial = false
            this.heatmap.on('plotly_click', e => {
                this.heatmap_x_value = e.points[0].x
                this.heatmap_y_value = e.points[0].y
                heatmap_click_callback()
            })
        }
    }
    
    updateHeatmapColor() {
        console.log(this.heatmap_color_select.value)
        let update = {
            colorscale: this.heatmap_color_select.value,
            reversescale: this.reversescale,
        }
        Plotly.restyle(this.heatmap.id, update)
    }
    
    createMap(data, pan_bounds) {
        console.log('DATA PASSED TO CREATE MAP:', data)
        // preventing Leaflet's "Map container is already initialized"
        // error when reloading the map by replacing old map div with a
        // new one. Working around the fact that for some reason 
        // checking for undefined or if initialized fails.
        this.old_map           = this.getElement('#map')
        this.new_map           = this.createElement('div')
        this.map_container     = this.getElement('#map_container')
        this.new_map.id        = 'map'
        this.map_container.removeChild(this.old_map)
        this.map_container.appendChild(this.new_map)
        this.polyline_color = this.map_toggle.checked ? 'blue' : 'white'
        
        let self = this
        
        this.map = L.map('map')
        if (self.map_toggle.checked) {
            L.tileLayer(
                'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 18,
            }).addTo(this.map)
        }
        
        for (let activity of data) {
            L.polyline(
                activity.polyline_decoded, {
                    color: this.polyline_color,
                    weight: 2,
                    opacity: activity.polyline_heat,
                    lineJoin: 'round',
                    // custom data used for tooltips, clicking on polylines etc.
                    activity_strava_link: activity.strava_link,
                    activity_name: activity.name,
                    activity_start_date: activity.start_date,
                    activity_id: activity.id,
                }
            )
            .addTo(this.map) 
            .addEventListener('click', function(e) {
                window.open(activity.strava_link)
                //polyline_click_handler(e)
            })
            .addEventListener('mouseover', function(e) {
                
                // change polyline color
                e.target.options.color = 'red'
                e.target.setStyle()
                
                // display tooltip
                self.polyline_tooltip.style.display = 'block'
                self.polyline_tooltip.style.top = `${self.mouse_y}px`
                self.polyline_tooltip.style.left = `${self.mouse_x}px`  
                self.polyline_tooltip.textContent = `${activity.name} (${activity.start_date})`
                //polyline_mouseover_handler(e)
                
                // highlight activity corresponding to the polyline in the table
                let rows = self.table.rowManager.activeRows
                rows.forEach(row => {
                    if (row.getData().id == activity.id) {
                        self.table.selectRow(row)
                    }
                })
            })
            .addEventListener('mouseout', function(e) {
                e.target.options.color = self.polyline_color
                e.target.setStyle()
                
                // unhighlight activity corresponding to the polyline in the table
                let rows = self.table.rowManager.activeRows
                rows.forEach(row => {
                    if (row.getData().id == activity.id) {
                        self.table.deselectRow(row)
                    }
                })
                
                // hide tooltip
                self.polyline_tooltip.style.display = 'none'
                //polyline_mouseout_handler(e)
            })
        }
        
        this.map.fitBounds(pan_bounds)
        
        //current_map = map // update global variable on each map creatio
    
    }
    
    createTable(data) {
        console.log('DATA PASSED TO CREATE ACTIVITY LIST:', data)
        
        let self = this
        
        this.table = new Tabulator("#table", {
            data: data,
            index: "Index",
            layout:"fitColumns",
            //placeholder: 'Click on heatmap to list activities',
            columns: [
                {title: 'Name', field: 'id', formatter: 'link', formatterParams: {
                        urlPrefix: 'https://www.strava.com/activities/',
                        labelField: 'name',
                    }
                },
                {title: 'Start date', field: 'start_date', formatter: 'datetime', formatterParams: {
                        inputFormat:"YYYY-MM-DD",
                        outputFormat:"DD/MM/YY",
                        invalidPlaceholder:"(invalid date)",
                    }
                },
                {title: 'Distance', field: 'distance'},
                {title: 'Moving time', field: 'moving_time'},
                {title: 'Average speed', field: 'average_speed'},
                {title: 'ID', field: 'id', visible: false},
            ],
            rowMouseOver: function(e, row) {
                self.color_polyline(row, 'red', 5, 1)
            },
            rowMouseOut: function(e, row) {
                self.color_polyline(row, self.polyline_color, 2, self.remembered_opacity)
            },
        }) 
        
        
    }
    
    color_polyline(row, target_color, target_weight, target_opacity) {
        
        let self = this
        
        this.map.eachLayer(function (polyline) {
            if (polyline.options.activity_id == row.getData().id) {
                
                // update the global, used on mouseout
                self.remembered_opacity = polyline.options.opacity
                
                polyline.options.color = target_color
                polyline.options.weight = target_weight//polyline.options.weight + 5
                polyline.options.opacity = target_opacity
                polyline.setStyle()
                // how to break the loop here, after the activity is found?
            }
        })
    }               
}

class Controller {
    constructor(model, view) {
        this.model = model
        this.view = view
        
        this.model.bindDataChanged(this.onDataChanged)
        this.view.bindHeatmapAxisChanged(this.handleHeatmapAxisChanged)
        this.view.bindHeatmapColorChanged(this.handleHeatmapColorChanged)
        this.view.bindMapLayerChanged(this.handleMapLayerChanged)
        this.view.bindMapToggleChanged(this.handleMapToggleChanged)
        
        this.initialize() 
    }
    
    async initialize() {
        console.log('initialize')
        this.model.data = await this.model.getData(this.view.inputs) 
        this.view.wait_message.style.display = 'none'
    }
    
    onDataChanged = data => {
        this.view.allowSelectOptions(data.allowed_select_options)  
        this.view.createHeatmap(data.heatmap, this.handleHeatmapAxisChanged)
        this.view.createMap(data.map, data.map_pan_bounds)
        this.view.createTable(data.table)
    }
    
    handleHeatmapAxisChanged = () => {
        this.initialize()
    }
    
    handleMapLayerChanged = () => {
        this.initialize()
    }
    
    handleMapToggleChanged = () => {
        console.log('fdfdf')
        this.initialize()
    }
    
    handleHeatmapColorChanged = () => {
        this.view.updateHeatmapColor()  
    }

}

const app = new Controller(new Model(), new View())
