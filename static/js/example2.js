function loadGantt(){
    $.ajax({
        url: '/motion_app/gantt_data',
        success: function (data, textStatus, jqXHR) {
            if ('error' in data) {
                alert("server error for " + "" + data['error'])
            }
            alert('success');
            data=data.data
            taskNames = data.map(function (x){return x.date});

            data.map(function (x){x["taskName"]=x.date})
            data.map(function (x){x["startDate"]=d3.time.second.offset(new Date("January 1, 2000 00:00:00"), x.startHour*60*60)})
            data.map(function (x){x["endDate"]=d3.time.second.offset(new Date("January 1, 2000 00:00:00"), x.endHour*60*60)})


            var taskStatus = {
                "SUCCEEDED" : "bar",
                "FAILED" : "bar-failed",
                "RUNNING" : "bar-running",
                "KILLED" : "bar-killed"
            };



            data.sort(function(a, b) {
                return a.endDate - b.endDate;
            });
            var maxDate = data[data.length - 1].endDate;
            data.sort(function(a, b) {
                return a.startDate - b.startDate;
            });
            var minDate = data[0].startDate;

            var format = "%H:%M";

            var gantt = d3.gantt().taskTypes(taskNames).taskStatus(taskStatus).tickFormat(format);
            //gantt.timeDomain([new Date("Sun Dec 09 04:54:19 EST 2012"),new Date("Sun Jan 09 04:54:19 EST 2013")]);
            //gantt.timeDomainMode("fixed");
            gantt(data);


        },
        error: function (err) {
            e = err
            alert("ajax error for " + "" + " error = " + err)
            btn.prop('disabled', false);
        }

    });

}

function addTask() {
    
    var lastEndDate = Date.now();
    if (data.length > 0) {
	lastEndDate = data[data.length - 1].endDate;
    }
    
    var taskStatusKeys = Object.keys(taskStatus);
    var taskStatusName = taskStatusKeys[Math.floor(Math.random()*taskStatusKeys.length)];
    var taskName = taskNames[Math.floor(Math.random()*taskNames.length)];
    lastEndDate = new Date("January 1, 2000 00:00:00")
    data.push({"startDate":d3.time.hour.offset(lastEndDate,Math.ceil(1*Math.random()))
               ,"endDate":d3.time.hour.offset(lastEndDate,(Math.ceil(Math.random()*3))+1)
               ,"taskName":taskName,"status":taskStatusName
            });
    gantt.redraw(data);
};

function removeTask() {
    data.pop();
    gantt.redraw(data);
};