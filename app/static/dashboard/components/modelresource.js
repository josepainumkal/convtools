var ModelResource = React.createClass({
  getInitialState: function(){
    return {
      type:'',
      name:'',
      url:''
    }
  },
  getResource: function(){
    var modelresourceUrl = this.props.url+'modelresources/'+this.props.id;
    $.ajax({
      url: modelresourceUrl,
      dataType: 'json',
      cache: false,
      success: function(data) {
          console.log('success!',data);
        this.setState({
          name: data['resource_name'],
          url:data['resource_url'],
          type:data['resource_type']
        });
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  componentDidMount: function(){
    this.getResource();
  },
  render: function() {
    return (
      <tr>
        <td>{this.state.type}</td>
        <td><a href={this.state.url} className="">{this.state.name}</a></td>
      </tr>
    );
  }
});

var ModelResourceList = React.createClass({
  render: function() {
    var apiUrl = this.props.url;
    var modelResourceNodes = this.props.data.map(function (modelresource) {
      return (
        <ModelResource url={apiUrl} id={modelresource.id}></ModelResource>
      );
    });
    return (
      <div className="model-resouces">
          <h4>{this.props.title}</h4>
          <ReactBootstrap.Table striped>
            <tbody>
            {modelResourceNodes}
            </tbody>
          </ReactBootstrap.Table>
      </div>
    );
  }
});

window.ModelResource=ModelResource
window.ModelResourceList=ModelResourceList
