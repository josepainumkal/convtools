  //var x = require('react')

var modelrunApi = {
  states_vars: {
    'NOT_STARTED': {
      'class': 'default',
      'iconClass': '',
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

var ModelRunBox = React.createClass({
  getInitialState: function() {
    var modelRunsByState={};
    $.each(modelrunApi.states_vars,function(key,val){
      modelRunsByState[key] = 0;
    });
    //console.log(modelRunsByState);
    return {
      data: [],apiUrl:this.props.apiUrl,url:this.props.url,
      query:this.props.query,modelresourceUrl:this.props.modelresourceUrl,
      pageNum:1,numPages:null,numModelRuns:null,modelRunsByState:modelRunsByState,userid:this.props.userid};
  },
  onModelRunCreate: function(){
    //this.getModelRuns(this.state.query);
    window.location.reload(true);
  },
  getModelRuns:function(query,pageNum){
    query = query || this.state.query;
    pageNum = pageNum || 1;
    var modelrunUrl = this.state.url+"?q="+JSON.stringify(this.state.query)+"&page="+pageNum;
    console.log('modelrun url:',modelrunUrl);
    $.ajax({
      url: modelrunUrl,
      dataType: 'json',
      cache: false,
      success: function(data) {
          //console.log('success!',data['objects'].length);
        this.setState({
          data: data['objects'],
          numPages:data.total_pages,
          pageNum:data['page'],
          numModelRuns:data['num_results']
        });
        this.getModelRunsCountByState();
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },

  getModelRunsCountByState:function(){
    //$self = this;
    // for(var state in this.state.modelRunsByState){
    //     this.getModelRunCountByState(state);
    // }
    var url = this.state.apiUrl+"users/"+this.state.userid+"/countsbystates";
    console.log(url);
    $.ajax({
      url: url,
      dataType: 'json',
      cache: false,
      success: function(data) {
          //console.log('success!',data['objects'].length);
        //var modelRunsByState = this.state.modelRunsByState;
        //modelRunsByState[state] = data['num_results'];
        this.setState({
          modelRunsByState:data
        });
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });


  },
  componentDidMount: function() {
      this.getModelRuns();
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
  OnPageSelect: function(event, selectedEvent){
    if(selectedEvent.eventKey==this.state.pageNum){
      return;
    }
    //console.log('yay!',selectedEvent.eventKey);
    //this.setState({pageNum:selectedEvent.eventKey});
    //console.log('pageNum',this.state.pageNum);
    this.getModelRuns(null,selectedEvent.eventKey);
  },
  render: function() {
    {/*var filters = Object.keys(modelrunApi.states_vars);
    var options=[<option value='ALL'>ALL</option>];
    $.each(filters,function(idx,val){
      options.push(<option value={val}>{val}</option>);
    });*/}
    console.log(this.state.modelRunsByState);
    var paginator;
    if(this.state.numPages>1){
      paginator = <div id="modelrunPaginator" className="text-center">
                    <ReactBootstrap.Pagination
                      items={this.state.numPages}
                      maxButtons={this.state.numPages}
                      activePage={this.state.pageNum}
                      onSelect={this.OnPageSelect} />
                  </div>
    }

    var modelrunForms=[]
    $.each(this.props.schemas,function(key,val){
      var modelrunForm = <ModelRunForm modelname={key} inputs={val['resources']['inputs']} onModelRunCreate={this.onModelRunCreate}
                      userid={this.props.userid} apiUrl={this.state.apiUrl}
                      modelrunUrl={this.state.url} modelresourceUrl={this.state.modelresourceUrl} />
      modelrunForms.push(modelrunForm);
    }.bind(this));
    return (
      <div className="modlerunBox">
          <div className="col-lg-12">
              <h1 className="page-header">
                  {this.props.title}
              </h1>
              <div className='row'>
                <div className='col-lg-3'>
                    <DashboardBox panelClass='panel-primary' iconClass='fa-tasks'
                      count={this.state.numModelRuns} descripiton='Total Model Runs' />
                </div>
                <div className='col-lg-3'>
                    <DashboardBox panelClass='panel-yellow' iconClass='fa-refresh'
                      count={this.state.modelRunsByState['RUNNING']} descripiton='Currently Running' />
                </div>
                <div className='col-lg-3'>
                    <DashboardBox panelClass='panel-red' iconClass='fa-exclamation-triangle'
                      count={this.state.modelRunsByState['ERROR']} descripiton='Failed Model Runs' />
                </div>
                <div className='col-lg-3'>
                    <DashboardBox panelClass='panel-green' iconClass='fa-thumbs-o-up'
                      count={this.state.modelRunsByState['FINISHED']} descripiton='Successful Runs' />
                </div>
              </div>

              {modelrunForms}
              {/* <ReactBootstrap.Input type="select" onChange={this.onFilter} label="">
                 {options}
                </ReactBootstrap.Input> */}
          </div>
          <div className="modleruns">
            {/*{paginator}*/}
            <ModelRunList onModelRunProgress={this.getModelRunsCountByState} apiUrl={this.state.apiUrl} url={this.state.url} data={this.state.data}  />
            {/*{paginator}*/}
          </div>
      </div>
    );
  }
});


window.ModelRunBox = ModelRunBox;
window.modelrunApi=modelrunApi
