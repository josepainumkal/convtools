var ModelRunForm = React.createClass({
  getInitialState:function(){
    var progressBars={}

    return {
      showModal:false,
      validationErrors:{},
      postingData:false,
      progressIconClass:'',
      progressText:'',
      progressBars:progressBars};
  },
  openModal:function(){
    this.setState({showModal:true});
  },
  closeModal:function(){
    if(!this.state.postingData){
      this.setState({showModal:false,progressText:''});
    }
  },
  validateInput:function(){
    var errors = {};
    var success=true;
    $.each(this.refs,function(key,val){
      if(!val.getValue().trim()){
        errors[key] = {'styleClass':'error'}
        success = false;
      }
      else{
        errors[key] = {'styleClass':''}
      }

    }.bind(this));

    return {'success':success,'errors':errors};

  },
  uploadResource:function(modelrunId,resource){
    var uploadUrl = this.props.modelrunUrl+"/"+modelrunId+"/"+this.props.modelresourceUrl;

    var formData = new FormData();
    $.each(resource,function(key,val){
      formData.append(key,val);
    });
    //var _this = this;
    return $.ajax({
          xhr: function(){
            var rtype=resource.resource_type
            var xhr = new window.XMLHttpRequest();
            //Upload progress
            xhr.upload.addEventListener("progress", function(evt){
              //console.log(resource.resource_type);
              if (evt.lengthComputable) {
                var percentComplete = (evt.loaded / evt.total)*100;
                var prog=$.extend({}, this.state.progressBars, {[resource.resource_type]:Math.floor(percentComplete)});
                this.setState({progressBars:prog});
              }
          }.bind(this), false);
          return xhr;
        }.bind(this),

        url:uploadUrl,
        type:'POST',
        contentType:false,
        processData: false,
        cache: false,
        data:formData,
        success: function(data) {

        }.bind(this),
        error: function(xhr, status, err) {
          console.error(uploadUrl, status, err.toString());
          console.error(xhr.responseText);
          this.setState({uploadError:true});
          {/*this.setState({postingData:false,progressIconClass:'',progressText:xhr.responseText});*/}
        }.bind(this)
      });

  },
  uploadResources:function(modelrunId,resources){
    var promises = [];
    $.each(resources,function(key,res) {
      var promise = this.uploadResource(modelrunId,res);
      promises.push(promise);
    }.bind(this));
    $.when.apply($, promises).done(function(){
          this.setState({postingData:false,progressIconClass:'',progressText:''});
          this.closeModal();
          this.props.onModelRunCreate();

    }.bind(this));
  },
  handleSubmit:function(e){
      e.preventDefault();
      var errors = this.validateInput();
      if(!errors.success){
        this.setState({validationErrors:errors.errors});
        return;
      }

      var modelrunData = {
          'title':this.refs.title.getValue().trim(),
          'model_name':this.refs.model_name.getValue().trim(),
          //'user_id':this.props.userid,
          'description':this.refs.description.getValue()
      };
      var resources=[];
      for(var ref in this.refs){
        var resouce={}
        if(ref in this.props.inputs){
          resouce['resource_type']=ref;
          resouce['file']=this.refs[ref].getInputDOMNode().files[0];
          resources.push(resouce);
        }
      }
      $.ajax({
        url: this.props.modelrunUrl,
        method:'POST',
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        cache: false,
        data:JSON.stringify(modelrunData),
        beforeSend: function(xhr){
          ajaxSetup.beforeSend(xhr);
          this.setState({postingData:true,progressIconClass:'fa fa-2x fa-spinner fa-spin',progressText:'Uploading Resource To Model Server'});
        }.bind(this),
        success: function(data) {
          this.uploadResources(data.id,resources);

        }.bind(this),
        error: function(xhr, status, err) {
          console.error(this.props.modelrunUrl, status, err.toString(),xhr.responseText);
          this.setState({postingData:false,progressIconClass:'',progressText:xhr.responseText});
          this.setState({uploadError:true});
        }.bind(this)
      });


  },
  render: function() {
      var progBars=[]
      $.each(this.state.progressBars,function(idx,val){
        var progBar=<ReactBootstrap.ProgressBar key={idx} active={true} now={val} label={idx+"  %(percent)s%"} />
        progBars.push(progBar);
      });

      var resouces = [];
      $.each(this.props.inputs,function(key,val){
        resouces.push(
          <ReactBootstrap.Input key={key}
          bsStyle={this.state.validationErrors[key]?this.state.validationErrors[key].styleClass:'success'}
          type="file" label={key} ref={key} />
        );
      }.bind(this));
      var uploadError;
      if(this.state.uploadaError){
        uploadError=<span>Error While Uploading</span>
      }
      return (
        <div id="#new-model-run">
          <div className="text-center margin-bottom">
            <ReactBootstrap.Button
              id="modelrunFormBtn"
              bsStyle="primary"
              bsSize="large"
              className="margin-bottom"
              onClick={this.openModal}>
              Create a New {this.props.modelname} Model Run
          </ReactBootstrap.Button>
          </div>

          <ReactBootstrap.Modal show={this.state.showModal} onHide={this.closeModal}>
            <ReactBootstrap.Modal.Header closeButton>
              <ReactBootstrap.Modal.Title>Create new {this.props.modelname} model run</ReactBootstrap.Modal.Title>
            </ReactBootstrap.Modal.Header>
            <ReactBootstrap.Modal.Body>
              <div className="modelrunForm-container">
                <form id="modelrunForm" onSubmit={this.handleSubmit} encType="multipart/form-data">
                  <ReactBootstrap.Input
                    bsStyle={this.state.validationErrors.title?this.state.validationErrors.title.styleClass:'success'}
                    type="text" label="Title" placeholder="Enter Title" ref="title" />
                    <ReactBootstrap.Input
                      type="hidden" value={this.props.modelname} ref="model_name" />
                    <ReactBootstrap.Input
                      type="textarea" label="Description" placeholder="Enter Description" ref="description" />
                  <h4>Input Resources</h4>
                  {resouces}
                  <ReactBootstrap.ButtonInput type="reset" value="Reset" />
                  <ReactBootstrap.ButtonInput type="submit" value="Submit" className='btn-success' />
                  {progBars}
                  {uploadError}
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

window.ModelRunForm=ModelRunForm
