var datasetShareApp = angular.module('datasetShareApp', []);

datasetShareApp.controller('DatasetShareCtrl', ['$scope', '$log', 
  function ($scope, $log) {
    $scope.modelRunName = "Yo mama";
    $scope.modelRunDescription = "Some good dro data";
    $scope.modelRunUUID = mrUUID;

    $log.log("uuid: " + mrUUID); // $scope.modelRunUUID);
}]);
