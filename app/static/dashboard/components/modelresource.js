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

var ModelResourceList = React.createClass({
  render: function() {
    var modelResourceNodes = this.props.data.map(function (modelresource) {
      return (
        <ModelResource data={modelresource}></ModelResource>
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
