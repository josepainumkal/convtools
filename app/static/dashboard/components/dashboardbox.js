
  var DashboardBox = React.createClass({

  render:function(){
    var iconClasses = 'fa fa-4x '+this.props.iconClass;
    var panelClasses = 'panel ' +this.props.panelClass;
    return (
      <div className={panelClasses}>
        <div className="panel-heading">
          <div className="row">
            <div className="col-xs-3">
              <i className={iconClasses}></i>
            </div>
            <div className="col-xs-9 text-right">
              <div className="huge">{this.props.count}</div>
              <div>{this.props.descripiton}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  });

  window.DashboardBox=DashboardBox
