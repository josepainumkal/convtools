/**
 Module for the file upload and insert page of the vw-webapp

 Author: Matthew A. Turner
 Date: Feb 23, 2016
**/


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

/**
    Handle Form Submit; React would be overkill, but I do want to prevent
    page reloads for better UX.
**/
$('form').submit(function(e) {
    e.preventDefault();

    //console.log($('form').serializeJSON());

    var formData = new FormData();
    var form = $('form').serializeArray();

    var modelrunUUID;
    for (var i = 0; i < form.length; i++)
    {
        if (form[i].name === 'modelrunUUID')
        {
            modelrunUUID = form[i].value;
        }
        formData.append(form[i].name, form[i].value);
    }

    formData.append('uploadedFile', $('#uploadedFile')[0].files[0]);

    var uploadUrl = '/api/modelruns/' + modelrunUUID + '/files';

    var values = $(this).serialize();
    $.ajax({
        method: 'post',
        url: uploadUrl,
        data: formData,
        processData: false,
        contentType: false
    })
    .done( function() {
        $('#upload-success-message').slideUp(function() {
            setTimeout(function() {
                $('#upload-success-message').slideDown();
            }, 4000)
        });
    })
    .fail(function() {
        $('#upload-fail-message').slideUp(function() {
            setTimeout(function() {
                $('#upload-fail-message').slideDown();
            }, 4000)
        });
    })
});
