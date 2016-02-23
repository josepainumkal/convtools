/**
 * Form for inserting new files and their metadata
 */
var InsertForm = React.createClass({

    getInitialState: function() {
        return {
            file: null,
            model: '',
            watershed: '',
            description: '',
            model_set: ''
        };
    },

    handleSubmit: function(e) {
        e.preventDefault();
        var file = this.state.file;
    },

    render: function() {
        return (
            <form onSubmit={this.handleSubmit} encType="multipart/form-data">
                <input type="file" onChange={this.handleFile} />
                <input type="text" />
                <input type="text" />
                <input type="text" />
                <input type="text" />
            </form>
        );
    }

});

/**
 * Box that contains the file list
 */
var FileListBox = React.createClass({

    loadFilesFromServer: function() {
        $.ajax({
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
                <h1>Attached Files</h1>
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

        var fileList =
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

        return (
            <div className="fileList">
                {fileList}
            </div>
        );
    }
});


window.FileListBox = FileListBox;
window.InsertForm = InsertForm;
