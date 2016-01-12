datasetShareApp
  .factory('uploadDataset', 
      ['Upload', '$http', '$timeout', '$q', '$log', 'VWP_CONFIG',
    function(Upload, $http, $timeout, $q, $log, VWP_CONFIG)
    {
      $log.log($http.defaults);
      $http.defaults.useXDomain = true;
      $http.defaults.withCredentials = true;
      $log.log($http.defaults);
      return function(file, modelRunUUID)
      {
        return $q(function(resolve, reject) {
          $log.log($http.defaults);
          // first upload the file to the virtual watershed
          file.upload = Upload.upload({
              method: 'POST',
              url: VWP_CONFIG.baseUrl + '/data',
              data: {
                file: file, 
                modelid: modelRunUUID,
                name: file.name
              },
              // credentials are in 'vwp' cookie put to browser by Flask
              headers: {
                'Authorization': authToken
              }
          });

          // handle file.upload promise
          file.upload.then(function (response) {
            $timeout(function () {
                file.result = response.data;
                resolve(file.result);
              });
            }, function (error) {
              if (error.status > 0)
              {
                reject(error.status + ': ' + error.data);
              }
            }, function (evt) {
              file.progress = 
                Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
            }
          );
        }); // end of $q for upload
      };
    }
])
  .factory('insertDatasetMetadata', ['$http', '$q', 'VWP_CONFIG',
    function($http, $q, VWP_CONFIG)    
    {
      return function(file, modelName, modelRunUUID, dates, description, 
                      watershedName, modelSet)
      {
        return $q(function(resolve, reject)
        {
          // now build and insert metadata for uploaded file
          $http({
              method: "POST",
              url: "/api/metadata/build",
            data: 
            {  
              input_file: file.name,
              model_name: modelName,
              model_run_uuid: modelRunUUID,
              start_datetime: dates.start.toISOString(),
              end_datetime: dates.end.toISOString(),
              description: description,
              watershed_name: watershedName,
              model_set: modelSet
            }
          }).then( 
            // if success, run another POST to insert to virtual watershed
            function (response) {

              $http({
                  url: VWP_CONFIG.baseUrl + '/datasets',
                  method: "PUT",
                  data: response.data
                }
              ).then( function(response) {
                resolve(response.data);
              }, function(error) {
                reject(error.data);
              }
              );
            },
            function (error) {
              reject(error.data);
            } 
          );
        });
      };
    }
]);
