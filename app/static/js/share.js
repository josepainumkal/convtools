var FileBox = React.createClass({

    loadFilesFromServer: function() {
        $.ajax({
            url: '/api/modelruns/c79b1d3a-4ddf-4d19-8ed6-068a86d2de7d/files',
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.setState({data: data});
                console.log(data);
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },

    getInitialState: function() {
        return {data: []};
    },

    componentDidMount: function() {
        this.loadFilesFromServer();
        setInterval(this.loadFilesFromServer, this.props.pollInterval);
    },

    render: function() {
        return (
            <div className="fileBox">
                <h1>Files</h1>
            </div>
        )
    }
});

window.FileBox = FileBox;
