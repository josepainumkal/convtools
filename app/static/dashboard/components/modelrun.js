var converter = new showdown.Converter();

var ModelRun = React.createClass({
  getInitialState: function() {

    var runButton;
    if (this.props.data.progress_state=='NOT_STARTED') {
      runButton = <ReactBootstrap.Button
                            onClick={this.onRunClick}
                            bsSize="large" className="run-btn"
                            bsStyle="primary">Run Model</ReactBootstrap.Button>;
    }

    if(this.props.data.progress_state=='RUNNING' || this.props.data.progress_state=='QUEUED'){
      var btnClass = this.getButtonClass(this.props.data.progress_state);
      runButton = <ReactBootstrap.Button
                      bsSize="large" className="run-btn"
                      bsStyle={btnClass['class']}>
                      <i className={btnClass['iconClass']}></i>
                      {this.props.data.progress_state}
                  </ReactBootstrap.Button>;

    }

    return {
      id: this.props.data.id,
      isRunning:false,
      progressBars: null,
      progressButton: runButton,
      resources: this.props.data.resources
    };
  },
  getButtonClass: function(state){
    return modelrunApi.states_vars[state];
  },
  componentDidMount:function(){
     if(this.props.data.progress_state=='RUNNING' || this.props.data.progress_state=='QUEUED'){
       this.intervalId = setInterval(this.getProgress, 2000);
     }
  },
  componentWillUpdate: function(nextProps,nextState){

  },
  getProgress: function(){
    var progUrl = this.props.apiUrl+"modelruns/"+this.state.id;
    var intervalId = this.intervalId;
    $.ajax({
      url: progUrl,
      method:'GET',
      dataType: 'json',
      cache: false,
      success: function(response) {
        var modelrun = response;
        var progress_events = response['progress_events'];

        var btnClass = this.getButtonClass(modelrun.progress_state);
        this.setState({progressButton:<ReactBootstrap.Button bsSize="large" className="run-btn" bsStyle={btnClass['class']}>
                                        <i className={btnClass['iconClass']}></i> {modelrun.progress_state}
                                      </ReactBootstrap.Button>});
        this.setState({isRunning:true});
        this.updateProgressBar(progress_events);
        if(modelrun.progress_state=='FINISHED'){
          this.setState({isRunning:false});
          clearInterval(intervalId);
          this.updateResource();
        }
        else if(modelrun.progress_state=='ERROR'){
          this.setState({isRunning:false});
          clearInterval(intervalId);
        }
        this.props.onModelRunProgress();

      }.bind(this),
      error: function(xhr, status, err) {
        console.error(startUrl, status, err.toString());
      }.bind(this)
    });

  },
  updateResource: function(){
    var modelrunUrl = this.props.apiUrl+'modelruns/'+this.state.id;
    $.ajax({
      url: modelrunUrl,
      method:'GET',
      dataType: 'json',
      cache: false,
      success: function(modelrun) {
        this.setState({resources:modelrun['resources']});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(startUrl, status, err.toString());
      }.bind(this)
    });

  },
  updateProgressBar: function(data){
    var progBars = [];
    if(data.length>0){
      for(var i=0;i<data.length;i++){
        var obj = data[i];
        var progVal = Math.floor(obj.progress_value);
        var active=false;
        if(progVal<100){
          var active=true;
        }
        var progBar = <ModelProgress active={active} progressVal={progVal} eventName={obj.event_name} eventDescription={obj.event_description} />;
        progBars.push(progBar);
        this.setState({progressBars:progBars});
      }
    }

  },

  onRunClick: function (event) {
    var startUrl  =this.props.url+"/"+this.props.data.id+"/start";
    $.ajax({
      url: startUrl,
      method:'PUT',
      dataType: 'json',
      cache: false,
      success: function(data) {
        var btnClass = this.getButtonClass('QUEUED');
        this.setState({isRunning:true});
        this.setState({progressButton:<ReactBootstrap.Button bsSize="large" className="run-btn" bsStyle={btnClass['class']}>
                                          <i className={btnClass['iconClass']}></i> QUEUED
                                        </ReactBootstrap.Button>});
        this.intervalId = setInterval(this.getProgress, 2000);

      }.bind(this),
      error: function(xhr, status, err) {
        console.error(startUrl, status, err.toString());
      }.bind(this)
    });


  },

  render: function() {
    var desc = converter.makeHtml(this.props.data.description);
    return (
      <div className="col-lg-12">
        <ReactBootstrap.Panel header={this.props.data.id +" "+ this.props.data.title}
          className="modelrun"  bsStyle="primary">
          <div className="col-lg-6">
            <ReactBootstrap.Table striped>
              <tr>
                <td>Title</td>
                <td> {this.props.data.title}</td>
              </tr>
              <tr>
                <td>Model</td>
                <td> {this.props.data.model_name}</td>
              </tr>
              <tr>
                <td>Status</td>
                <td> {this.props.data.progress_state}</td>
              </tr>
            </ReactBootstrap.Table>
            <div className="modelrundesc" >
                <h4>Description</h4>
                 <div dangerouslySetInnerHTML={{__html: desc}} ></div>
              </div>

            <ModelResourceList title='Resources' url={this.props.apiUrl} data={this.state.resources} />
            <ReactBootstrap.Button
                                onClick={this.props.onDelete}
                                bsSize="small" className="run-btn"
                                bsStyle="danger">Delete</ReactBootstrap.Button>
            <div className="logbox">
              { this.props.data.logs && <h3>Logs</h3> }
              { this.props.data.logs }
            </div>
          </div>
          <div ref="runBtn" className="col-lg-6 margin-bottom">
            {this.state.progressButton}
          </div>
          <div className="col-lg-6" ref="progressbarcontainer">
            {this.state.progressBars}
          </div>

        </ReactBootstrap.Panel>
      </div>
    );
  }
});


var ModelRunList = React.createClass({
  onDelete:function(modelrun) {
    if(this.refs[modelrun.id].state.isRunning){
      alert("You can't delete a run while model is running");
      return;
    }
    var descision=confirm("Are you sure you want to delete the model run?");
    if(descision){
      $.ajax({
        url: this.props.url+'/'+modelrun.id,
        type: 'DELETE',
        success: function(result) {
          window.location.reload(true);
        }
      });
    }


  },
  render: function() {
    var url = this.props.url;
    var apiUrl = this.props.apiUrl;
    var onModelRunProgress = this.props.onModelRunProgress;
    var modelrunNodes = this.props.data.map(function (modelrun) {
      return (
        <ModelRun ref={modelrun.id} onDelete={this.onDelete.bind(this, modelrun)}
          onModelRunProgress={onModelRunProgress}
          apiUrl={apiUrl}  url={url}
          data={modelrun}>

        </ModelRun>
      );
    }.bind(this));
    return (
      <div className="modelrunList">
        {modelrunNodes}
      </div>
    );
  }
});


window.ModelRun=ModelRun;
window.ModelRunList=ModelRunList;
