class Model {
    constructor(){}
       
    async getActivityLeaderboards(activity_id, date_ranges, callback) {
        let url = new URL(leaderboards_data_absurl)
        let params = {
            'activity_id': activity_id,
            'date_ranges': date_ranges,                       
        }
        console.log(activity_id, date_ranges)
        url.search = new URLSearchParams(params)
        const response = await fetch(url)
        const json = await response.json()
        callback(json.segment_leaderboards)
        return json
    }
    
}

class View {
    constructor() {
        this.activity_select = this.getElement('#activity_select')
        this.submit_button   = this.getElement('#get_leaderboards_button')
        this.msg             = this.getElement('#msg')
        this.segment_rows    = this.getElement('#segment_rows') 
        this.checkboxes      = document.querySelectorAll('#date_inputs input')
        this.footer          = this.getElement('#footer')
    }
    
    getElement(selector) {
        let element = document.querySelector(selector)
        return element
    }
    
    createElement(tag, className) {
        let element = document.createElement(tag)
        if (className) element.className = className
        return element
    }
    
    bindSubmitButtonClicked(handler) {
        this.submit_button.addEventListener('click', e => {
            this.activity_select.disabled = true // disable select while request is being made
            this.msg.className = 'visible'
            this.segment_rows.innerHTML = ''
            let activity_id = this.activity_select.value
            handler(activity_id, this.date_ranges)
        })    
    }
    
    get date_ranges() {
        let d_ranges = []
        this.checkboxes.forEach(checkbox => {
            if (checkbox.checked == true) {
                d_ranges.push(checkbox.value)
            }
        })
        return d_ranges
    }
    
    createSegmentMap(div, decoded_polyline) {
        var map = L.map(div, {'zoomControl': false})
        L.tileLayer(
            'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
        }).addTo(map)
        
        var polyline = L.polyline(decoded_polyline).addTo(map)
        map.fitBounds(polyline.getBounds())
    }
    
    createTables(leaderboards) {
        leaderboards.forEach(leaderboard => {
            this.createLeaderboardTable(leaderboard)
        })
    }
    
    createLeaderboardTable(leaderboard) {
        let segment_row        = this.createElement('div')
        let segment_row_header = this.createElement('div')
        let segment_link       = this.createElement('a')
        let segment_map        = this.createElement('div')
        let segment_row_tables = this.createElement('div')
        
        segment_row.className          = "segment_row"
        segment_row_header.className   = "segment_row_header"
        segment_link.className         = "header_hyperlink"
        segment_link.href              = leaderboard.segment_strava_link
        segment_link.textContent       = leaderboard.segment_name
        segment_map.className          = 'segment_map'
        segment_row_tables.className   = "segment_row_tables"
        
        segment_row_header.appendChild(segment_link)
        segment_row.appendChild(segment_row_header)
        segment_row.appendChild(segment_map)
        segment_row.appendChild(segment_row_tables)
        segment_rows.appendChild(segment_row)
        
        this.createSegmentMap(segment_map, leaderboard.segment_polyline)
        
        this.date_ranges.forEach(date_range => {                      
            let entries = leaderboard.entries[date_range]
            if (date_range == '') { 
                date_range = 'all_time' // so that "All time" table has header as well
            }
            
            let table_container = this.createElement('div')
            let table_header    = this.createElement('div')
            let table_contents  = this.createElement('div')
            
            table_container.className = 'segment_table_container'
            table_contents.id         = makeid(10)
            table_header.className    = 'segment_table_container_header'
            table_header.textContent  = capitalize(date_range.replace('_', ' '))
            
            table_container.appendChild(table_header)
            table_container.appendChild(table_contents)
            segment_row_tables.appendChild(table_container)
            
            let table = new Tabulator('#' + table_contents.id, {
                data: entries,
                index: "Index",
                layout:"fitData",
                columns:[
                    {title: 'Athlete', field: 'athlete_name'}, //,formatter: 'link'},
                    {title: 'Start date', field: 'start_date', formatter: 'datetime', formatterParams: {
                            inputFormat:"YYYY-MM-DD",
                            outputFormat:"DD/MM/YY",
                            invalidPlaceholder:"(invalid date)",
                        }
                    },
                    {title: 'Elapsed time', field: 'elapsed_time'},
                    {title: 'Moving time', field: 'moving_time'},
                ]
            })   
        })
    }
    
    hideFooter() {
        this.footer.style.display = 'none'
    }
}
    
class Controller {
    constructor (model, view){
        this.model = model
        this.view = view
        this.view.bindSubmitButtonClicked(this.handleSubmitButtonClicked)
    }
    
    handleSubmitButtonClicked = (activity_id, date_ranges) => {
        this.model.getActivityLeaderboards(activity_id, date_ranges, this.onLeaderboardsReceived)
    }
    
    onLeaderboardsReceived = leaderboards => {
        console.log('LEADERBOARDS', leaderboards)
        this.view.createTables(leaderboards) 
        this.view.activity_select.disabled = false
        this.view.msg.className = 'hidden'
        this.view.hideFooter()
    }
}

// helpers
function makeid(length) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
   var charactersLength = characters.length;
   for (var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}
    
function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1)
}

const app = new Controller(new Model(), new View())












