var datasetShareApp = 
  angular.module('datasetShareApp', ['ngFileUpload', 'ui.date'])
         .config( ['$httpProvider', function ($httpProvider) {
            $httpProvider.defaults.withCredentials = true;
         }]);

datasetShareApp.controller('DatasetShareCtrl', 
  ['$scope', '$log', 'Upload', '$timeout', '$http',
  function ($scope, $log, Upload, $timeout, $http) {

    // these are set in templates/share/datasets.html in head_ext block
    $scope.modelRunName = mrName;
    $scope.modelRunDescription = mrDesc;
    $scope.modelRunUUID = mrUUID;

    //var $scope.inputFile, $scope.modelName, $scope.modelRunUUID, 
      //$scope.startDateTime, $scope.endDateTime, $scope.description, 
      //$scope.watershedName, $scope.modelSet;

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
      $log.log(file.name);
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
     * @param {string} file - file object for upload
     * @returns {string} JSON string of properly formatted gstor-ready
     *  metadata for the inputFile
     */
    $scope.uploadStatus = "None yet";
    $scope.pushStatus = "None yet";

    $scope.pushToGstor = function(file)
    {
      baseUrl = 'https://vwp-dev.unm.edu/apps/vwp';

      // first upload the file to the virtual watershed
      file.upload = Upload.upload({
          url: baseUrl + '/data',
          data: {
            file: file, 
            model_run_uuid: $scope.modelRunUUID,
          },
          // credentials are in 'vwp' cookie put to browser by Flask
          withCredentials: true
      });

      // handle file.upload promise
      file.upload.then(function (response) {
        $timeout(function () {
            file.result = response.data;
            $scope.uploadStatus = response.data;
          });
        }, function (error) {
          if (error.status > 0)
          {
            $scope.errorMsg = error.status + ': ' + error.data;
            $scope.uploadStatus = error.status + ': ' + error.data;
          }
        }, function (evt) {
          file.progress = 
            Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
        }
      );


      // now build and insert metadata for uploaded file
      $http({
          method: "POST",
          url: "/api/metadata/build",
        data: 
        {  
          input_file: file.name, //"yo.txt", //$scope.file.name,
          model_name: $scope.modelName,
          model_run_uuid: $scope.modelRunUUID,
          start_datetime: $scope.dates.start.toISOString(),
          end_datetime: $scope.dates.end.toISOString(),
          description: $scope.description,
          watershed_name: $scope.watershedName,
          model_set: $scope.modelSet
        }
      }).then( 
        // if success, run another POST to insert to virtual watershed
        function (response) {

          $scope.metadataResult = response.data;

          $http({
              url: baseUrl + '/datasets',
              method: "POST",
              data: response.data,
              withCredentials: true
            }
          ).then( function(response) {
            $scope.pushStatus = response.data;
          }, function(error) {
            $scope.pushStatus = 'in metadata insert:\n' + error.data;
          }
          );
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
