
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

window.ModelProgress=ModelProgress
