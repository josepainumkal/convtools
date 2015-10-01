  var modelrunApi = {
    states_vars: {
            'NOT_STARTED': {
                'class': 'default',
                'iconClass': ''
            },
            'QUEUED': {
                'class': 'info',
                'iconClass': 'fa fa-spinner fa-spin'
            },
            'RUNNING': {
                'class': 'warning',
                'iconClass': 'fa fa-refresh fa-spin'
            },
            'ERROR': {
                'class': 'danger',
                'iconClass': 'fa fa-exclamation-triangle'
            },
            'FINISHED': {
                'class': 'success',
                'iconClass': 'fa fa-thumbs-up'
            }
        }
    
  };

  var ModelRun = React.createClass({
    getInitialState: function() {
      var inputResources = $.grep(this.props.data.resources, function (element, index) {
        return element.resource_type == 'input';
      });
      var runButton;
      if (this.props.data.progress_state=='NOT_STARTED' && inputResources.length>0) {
        //console.log(this.props.id);
        //var style = {'display':'inline-block'};
        runButton = <ReactBootstrap.Button onClick={this.onRunClick} bsSize="large" className="run-btn" bsStyle="primary">Run Model</ReactBootstrap.Button>;
      }

      if(this.props.data.progress_state=='RUNNING'){
        var btnClass = this.getButtonClass('RUNNING');
        runButton = <ReactBootstrap.Button bsSize="large" className="run-btn" bsStyle={btnClass['class']}>
                                          <i className={btnClass['iconClass']}></i> 
                                          {this.props.data.progress_state}
                                        </ReactBootstrap.Button>; 
        //this.getProgress();
        this.intervalId = setInterval(this.getProgress, 2000);
      }

      return {id:this.props.data.id,progressBars:null,progressButton:runButton,inputResources:inputResources,resources:this.props.data.resources};
    },
    getButtonClass: function(state){
    
      return modelrunApi.states_vars[state];
    },
    componentWillUpdate: function(nextProps,nextState){
        console.log('updated',nextState);
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

          this.updateProgressBar(progress_events);
          if(modelrun.progress_state=='FINISHED'){
            clearInterval(intervalId);
            this.updateResource(modelrun.id);
          }
          else if(modelrun.progress_state=='ERROR'){
            clearInterval(intervalId);
            //this.updateResource(progress_events[0].modelrun_id);
          }

        }.bind(this),
        error: function(xhr, status, err) {
          console.error(startUrl, status, err.toString());
        }.bind(this)
      });

    },
    updateResource: function(modelrunId){
      var modelrunUrl = this.props.apiUrl+'modelruns/'+modelrunId;
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
      //console.log('data inside update:',data);
      if(data.length>0){
        //console.log('in if:',data);
        for(var i=0;i<data.length;i++){
          var obj = data[i];
          //console.log('obj prog:',obj.progress_value);
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
      //console.log('Run Button clicked');
      var startUrl  =this.props.url+"/"+this.props.data.id+"/start";
      //this.intervalId = setInterval(this.getProgress, 5000);
      $.ajax({
        url: startUrl,
        method:'PUT',
        dataType: 'json',
        cache: false,
        success: function(data) {
          var btnClass = this.getButtonClass('QUEUED');
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
      //console.log('bakkas');
      return (
        <div className="col-lg-12">
          <ReactBootstrap.Panel header={this.props.data.id +" "+ this.props.data.title} className="modelrun"  bsStyle="primary">
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
              
              <ModelResourceList title='Resources' data={this.state.resources} />
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

  var ModelResource = React.createClass({
    render: function() {
      return (
        <tr> 
            <td>{this.props.data.resource_type}</td>
            <td><a href={this.props.data.resource_url} className="">{this.props.data.resource_name}</a></td> 
          
        </tr>
      );
    }
  });

  var ModelProgress = React.createClass({

    render: function() {
      return (
        <div className='progress-event'>
          {this.props.eventDescription}
          <ReactBootstrap.ProgressBar active={this.props.active} now={this.props.progressVal} label="%(percent)s%" />
        </div>
      );
    }
  });
  var ModelRunBox = React.createClass({
    getInitialState: function() {
      return {data: [],apiUrl:this.props.apiUrl,url:this.props.url,query:this.props.query,modelresourceUrl:this.props.modelresourceUrl};
    },
    onModelRunCreate: function(){
      this.getModelRuns(this.state.query);
    },
    getModelRuns:function(query){
      $.ajax({
        url: this.state.url+"?q="+JSON.stringify(query),
        dataType: 'json',
        cache: false,
        success: function(data) {
            console.log('success!');
          this.setState({
            data: data['objects']
          });
        }.bind(this),
        error: function(xhr, status, err) {
          console.error(this.props.url, status, err.toString());
        }.bind(this)
      });     
    },
    componentDidMount: function() {
        this.getModelRuns(this.state.query);
    },
    
    onFilter: function(event){
      //console.log('changed to',event.target.value);
      if(event.target.value != 'ALL'){
        var q= jQuery.extend({}, this.state.query);
        var baseFilter = q.filters[0];
        q.filters=[baseFilter,{"name":"progress_state","op":"eq","val":event.target.value}];
        this.getModelRuns(q);
      }else{
        this.getModelRuns(this.state.query);
      }   

    },
    render: function() {
      var filters = Object.keys(modelrunApi.states_vars);
      var options=[<option value='ALL'>ALL</option>];
      $.each(filters,function(idx,val){
        options.push(<option value={val}>{val}</option>);
      });
      //console.log('rerendered');
      return (
        <div className="modlerunBox">
            <div className="col-lg-12">
                <h1 className="page-header">
                    Your Model Runs
                </h1>
                <ModelRunForm onModelRunCreate={this.onModelRunCreate} userid={this.props.userid} apiUrl={this.state.apiUrl} modelrunUrl={this.state.url} modelresourceUrl={this.state.modelresourceUrl} />
                {/* <ReactBootstrap.Input type="select" onChange={this.onFilter} label="">
                   {options}
                  </ReactBootstrap.Input> */}
            </div>
            <div className="modleruns">
              <ModelRunList apiUrl={this.state.apiUrl} url={this.state.url} data={this.state.data}  />
            </div>
        </div>
      );
    }
  });

  var ModelRunList = React.createClass({

    render: function() {
      var url = this.props.url;
      var apiUrl = this.props.apiUrl;
      var modelrunNodes = this.props.data.map(function (modelrun) {
        
        return (
          <ModelRun apiUrl={apiUrl}  url={url} data={modelrun}>
           
          </ModelRun>
        );
      });
      return (
        <div className="modelrunList">
          {modelrunNodes}
        </div>
      );
    }
  });  

  var ModelResourceList = React.createClass({
    render: function() {
      var modelResourceNodes = this.props.data.map(function (modelresource) {
        return (
          <ModelResource data={modelresource}>
          </ModelResource>
        );
      });
      return (
        <div className="model-resouces">
            <h4>{this.props.title}</h4>
            <ReactBootstrap.Table striped>
                {modelResourceNodes}
            </ReactBootstrap.Table>
        </div>
        
      );
    }
  });  

  var ModelRunForm = React.createClass({
    getInitialState:function(){

      return {showModal:false,validationErrors:{},postingData:false,progressIconClass:'',progressText:''};
    },
    openModal:function(){
      this.setState({showModal:true});
    },
    closeModal:function(){
      if(!this.state.postingData){
        this.setState({showModal:false});
      }
      
    },
    validateInput:function(formData){
      var errors = {};
      var success=true;
      for(var field in formData){
        if(!formData[field].getValue().trim()){
          errors[field] = {'styleClass':'error'}
          success = false;
        }
        else{
          errors[field] = {'styleClass':''}
        }
      }
      return {'success':success,'errors':errors};

    },
    uploadResource:function(modelrunId,resource){
      var uploadUrl = this.props.modelrunUrl+"/"+modelrunId+"/"+this.props.modelresourceUrl;
      console.log('upload url',uploadUrl);
      console.log(resource);
      var formData = new FormData();
      $.each(resource,function(key,val){
        console.log(key,val);
        formData.append(key,val);
        console.log(formData);
      });
      
      $.ajax({
          url:uploadUrl,
          type:'POST',
          contentType:false,
          processData: false,
          cache: false,
          data:formData,
          success: function(data) {
            console.log('done resource!',data);
            this.setState({postingData:false,progressIconClass:'',progressText:''});
            this.closeModal();
            this.props.onModelRunCreate();

          }.bind(this),
          error: function(xhr, status, err) {
            console.error(uploadUrl, status, err.toString());
            console.error(xhr.responseText);
          }.bind(this)
        });

    },
    handleSubmit:function(e){
        e.preventDefault();
        var formData={};
        for(var ref in this.refs){
          console.log(this.refs[ref])
          formData[ref] = this.refs[ref];
        }
        var errors = this.validateInput(formData);
        console.log(errors);
        if(!errors.success){
          this.setState({validationErrors:errors.errors});
          return;
        }

        var modelrunData = {'title':formData['title'].getValue().trim(),'model_name':formData['model_name'].getValue().trim(),'user_id':this.props.userid};
        var modelResourceData =  {'file':formData['file'].getInputDOMNode().files[0],'resource_type':formData['resource_type'].getValue()};
        
        $.ajax({
          url: this.props.modelrunUrl,
          method:'POST',
          dataType: 'json',
          contentType: 'application/json; charset=utf-8',
          cache: false,
          data:JSON.stringify(modelrunData),
          beforeSend: function(){
            this.setState({postingData:true,progressIconClass:'fa fa-2x fa-spinner fa-spin',progressText:'Uploading Resource To Model Server'});
          }.bind(this),
          success: function(data) {
            console.log(data);
            this.uploadResource(data.id,modelResourceData);

          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.modelrunUrl, status, err.toString(),xhr.responseText);
            
          }.bind(this)
        });


    },
    render: function() {

        return (  
          <div id="#new-model-run">
            <ReactBootstrap.Button
              id="modelrunFormBtn"
              bsStyle="primary"
              bsSize="large"
              className="margin-bottom"
              onClick={this.openModal}>
              Create a New Model Run
              
            </ReactBootstrap.Button>
            <ReactBootstrap.Modal show={this.state.showModal} onHide={this.closeModal}>
              <ReactBootstrap.Modal.Header closeButton>
                <ReactBootstrap.Modal.Title>Create new model run</ReactBootstrap.Modal.Title>
                
              </ReactBootstrap.Modal.Header>
              <ReactBootstrap.Modal.Body>
                <div className="modelrunForm-container">
                  <form id="modelrunForm" onSubmit={this.handleSubmit} encType="multipart/form-data">
                    <ReactBootstrap.Input bsStyle={this.state.validationErrors.title?this.state.validationErrors.title.styleClass:''} type="text" label="Title" placeholder="Enter Title" ref="title" />
                    <ReactBootstrap.Input type="select" label="Model Name" ref="model_name">
                      <option value="isnobal">isnobal</option>
                    </ReactBootstrap.Input>
                    <ReactBootstrap.Input type="select" label="Resource Type" ref="resource_type">
                      <option value="input">input</option>
                    </ReactBootstrap.Input>
                    <ReactBootstrap.Input bsStyle={this.state.validationErrors.file?this.state.validationErrors.file.styleClass:''} type="file" label="Input Resource" help="Select a netcdf file that complies with iSNOBAL" ref="file" />
                    <ReactBootstrap.ButtonInput type="reset" value="Reset" />
                    <ReactBootstrap.ButtonInput type="submit" value="Submit" className='btn-success' />
                    <span><i className={this.state.progressIconClass}></i> {this.state.progressText}</span>
                  </form>
                </div>
              </ReactBootstrap.Modal.Body>
              <ReactBootstrap.Modal.Footer>
                <ReactBootstrap.Button onClick={this.closeModal}>Close</ReactBootstrap.Button>
              </ReactBootstrap.Modal.Footer>
            </ReactBootstrap.Modal>
          </div>   
            
        ); 
    }
  });  

  var userId= $('#modelruns-container').data('user-id')
  var apiUrl = "http://vwadaptor.ddns.net:5000/api/"
  var modelrunsQuery = {
    "filters": [{
      "name": "user_id",
      "op": "eq",
      "val": userId
    }],
    "order_by": [{
      "field": "created_at",
      "direction":"desc"
    }]
  };
  var modelrunsUrl = apiUrl+"modelruns";
  
  var modelresourceUrl = "upload";

  React.render(
     <ModelRunBox apiUrl={apiUrl} 
            url={modelrunsUrl} 
            modelresourceUrl={modelresourceUrl} 
            query={modelrunsQuery} 
            userid={$('#modelruns-container').data('user-id')} />,
    document.getElementById('modelruns-container')
  );