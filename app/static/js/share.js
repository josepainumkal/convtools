/**
 * Box that contains the file list
 */
var FileBox = React.createClass({

    loadFilesFromServer: function() {
        $.ajax({
            //url: '/api/modelruns/c79b1d3a-4ddf-4d19-8ed6-068a86d2de7d/files',
            url: this.props.baseUrl + this.props.modelrunUUID + '/files',
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
        return {
            data: {files: []}
        };
    },

    componentDidMount: function() {
        this.loadFilesFromServer();
        setInterval(this.loadFilesFromServer, this.props.pollInterval);
    },

    render: function() {
        return (
            <div className="fileBox">
                <h1>Files</h1>
                <FileList data={this.state.data} />
            </div>
        )
    }
});


/**
 * File list contained within the box
 */
var FileList = React.createClass({

    render: function() {
        console.log(this.props.data.files);
        var tableRows = this.props.data.files.map(function(file) {

            return (
                <tr key={file.uuid}>
                    <td>{file.name}</td>
                    <td>{file.last_modified}</td>
                    <td className="download-link">
                        <a href={file.url}>Download</a>
                    </td>
                </tr>
            );
        });

        return (

            <div className="fileList">
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <td><b>File Name</b></td>
                            <td><b>Last Modified</b></td>
                            <td className="download-link"><b>Download Link</b></td>
                        </tr>
                    </thead>
                    <tbody>
                        {tableRows}
                    </tbody>
                </table>
            </div>
        );
    }
});


window.FileBox = FileBox;
