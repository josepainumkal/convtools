
var ModelProgress = React.createClass({

  render: function() {
    var desc = this.props.eventDescription.replace(/\n/g, "<br />");
    return (
      <div className='progress-event'>
        <div className="logbox" dangerouslySetInnerHTML={{__html: desc}}></div>
        <ReactBootstrap.ProgressBar active={this.props.active} now={this.props.progressVal} label="%(percent)s%" />
      </div>
    );
  }
});

window.ModelProgress=ModelProgress
