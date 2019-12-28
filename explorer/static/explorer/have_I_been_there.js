class Model {   
    async get_data(form_data) {
        let response = await fetch(have_I_been_there_URL, {
            method: 'POST',
            body: form_data,
            credentials: 'same-origin',
        })
        let json = await response.json()
        return json
    }
}

class View {
    constructor() {
        
        this.wait_modal = {
            el: document.getElementById('wait_modal'),
            show() {
                this.el.style.display = 'flex'
            },
            hide() {
                this.el.style.display = 'none'
            },
            //~ attach: async function(f) {
                //~ this.show()
                //~ await f
                    //~ .then(() => this.hide())
            //~ },
        }
        
        this.form = {
            el: document.getElementById('gpx_upload_form'),
            file: function() {
                return document.getElementById('file_input').files[0]
            },
            radius: function() {
                return document.getElementById('radius_input').value
            },
            onSubmit(e) {
                e.preventDefault()
                let form_data = new FormData()
                if (!demo_mode) {
                    form_data.append('file', this.file())
                } else {
                    let filename = document.getElementById('file_select').value
                    form_data.append('filename', filename)
                }
                form_data.append('radius', this.radius())
                form_data.append('csrfmiddlewaretoken', csrf_token)
                return form_data
            },
        }
        
        this.plot = {
            el: document.getElementById('map'),
            layout: {
                title: 'The whiter the line part is, the more frequently visited has it been',
                font: {
                    family: 'BebasNeueRegular',
                    color: 'rgb(150, 150, 150)',
                },
                showlegend: false,
                annotations: [],
                paper_bgcolor: 'black',
                plot_bgcolor: 'rgba(0,0,0,0)',
                width: 700,
                xaxis: {
                    title: {
                        text: 'Longitude'
                    },
                },
                yaxis: {
                    title: {
                        text: 'Latitude',
                    },          
                },
            },
            plot(lines) {
                let traces = []
                for (let line of lines) {
                    let c = line.coordinates
                    let trace = {
                        y: [c[0][0], c[1][0]],
                        x: [c[0][1], c[1][1]],
                        type: 'scatter',
                        mode: 'lines',
                        line: {
                            color: 'white',
                        },
                        opacity: line.opacity,
                    }
                    traces.push(trace)
                }
                Plotly.newPlot(this.el.id, traces, this.layout);
            },
        }
        
        this.leaflet_map = {
            el: document.getElementById('leaflet_map'),
            create(coordinates) {
                console.log('creating leaflet')
                let map = L.map(this.el)
                console.log(map)
                L.tileLayer(
                    'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 18,
                }).addTo(map)
                let polyline = L.polyline(coordinates).addTo(map)
                map.fitBounds(polyline.getBounds())
            }
        }   
    }
    
    bindFormSubmit(handler) {
        this.form.el.addEventListener('submit', e => {
            let form_data = this.form.onSubmit(e)
            handler(form_data)
        })
    }
}

class Controller {
    constructor(model, view) {
        this.model = model
        this.view = view
        this.view.bindFormSubmit(this.formSubmitHandler)     
    }
    
    formSubmitHandler = async(form_data) => {
        this.view.wait_modal.show()
        let plot_data = await this.model.get_data(form_data)
        this.view.wait_modal.hide()
        this.view.plot.plot(plot_data.lines)
        this.view.leaflet_map.create(plot_data.coordinates)
    }
}

let app = new Controller(new Model(), new View())
