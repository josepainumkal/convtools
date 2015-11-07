var datasetShareApp = angular.module('datasetShareApp', ['ngFileUpload', 'ui.date']);

datasetShareApp.controller('DatasetShareCtrl', 
  ['$scope', '$log', 'Upload', '$timeout', '$http',
  function ($scope, $log, Upload, $timeout, $http) {
    $scope.modelRunName = "Yo mama";
    $scope.modelRunDescription = "Some good dro data";

    $scope.modelRunUUID = mrUUID;
    
    // set date options and initialize start/end dates
    $scope.dateOptions = {
        changeYear: true,
        changeMonth: true,
        yearRange: '1900:+10'
    };

    $scope.dates = {
      start: new Date(2010, 0, 1),
      end: new Date(2011, 8, 30)
    };

    // create time picker vars
    $scope.hours = [];
    for (var i = 0; i < 24; i++)
      $scope.hours.push(i);

    $scope.uploadPic = function(file) 
    {
      file.upload = Upload.upload({
          url: 'https://angular-file-upload-cors-srv.appspot.com/upload',
          data: {
            file: file, username: $scope.username
          }
      });
      
      file.upload.then(function (response) {
        $timeout(function () {
          file.result = response.data;
          });  
        }, function (response) {
          if (response.status > 0)
          {
            $scope.errorMsg = response.status + ': ' + response.data;
          }
        }, function(evt) {
          // Math.min is IE hack to prevent 200% from being displayed
          file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
        });
    };

    /**
     * Fetches full gstor metadata from the server. 
     * @param {string} inputFile - name of the input file
     * @param {string} modelName - hydrological model name; one of 'isnobal',
     *  'prms', or 'HydroGeoSphere'; capitalization enforced
     * @param {string} modelRunUUID - unique model run identifier recieved from
     *  gstor
     * @param {Date} startDatetime - temporal start of the dataset being pushed
     * @param {Date} endDatetime - temporal end of the dataset being pushed
     * @param {string} description - desc. of the dataset being pushed
     * @param {string} watershedName - name of the watershed where the data
     *  comes from. One of 'Reynolds Creek', 'Dry Creek', 'Valles Caldera',
     *  or 'Lehman Creek' with capitalization enforced.
     * @param {string} modelSet - gstor speak for 'inputs', 'outputs', or 
     *  'reference'
     * @returns {string} JSON string of properly formatted gstor-ready
     *  metadata for the inputFile
     */
    $scope.fetchGstorMetadata = function(inputFile, 
                                         modelName, 
                                         modelRunUUID, 
                                         startDateTime,
                                         endDateTime,
                                         description,
                                         watershedName,
                                         modelSet)
    {
      $http({
          method: "POST",
          url: "/api/metadata/build",
        data: 
        {  
          input_file: inputFile,
          model_name: modelName,
          model_run_uuid: modelRunUUID,
          start_datetime: startDateTime.toISOString(),
          end_datetime: endDateTime.toISOString(),
          description: description,
          watershed_name: watershedName,
          model_set: modelSet
        }
      }).then( 
        function (response) {
          $scope.metadataResult = response.data;
        },
        function (error) {
          $scope.metadataResult = error.data;
        } 
      );
    };

    $scope.metadataResult = 'test';

    $scope.testFetchGstorMetadata = function()
    {
      return $scope.fetchGstorMetadata('test.txt', 'isnobal', 'xxx-xxxx', 
        new Date(2001, 0, 1), new Date(2001, 11, 31), 'some data', 
          'Dry Creek', 'inputs');
    };
}]);
