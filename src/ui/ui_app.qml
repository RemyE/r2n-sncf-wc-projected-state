import QtQuick
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "components/"
import "graphic/"


Window {
    id: window
    minimumWidth: 960
    minimumHeight: 540
    title: "SNCF-toilet-data-analyser"
    color: window.backgroundColor

    // Propriété sur les couleurs
    property string backgroundColor: "#000000"

    // Fonctions pour changer la page active
    function return() {
        operation.visible = false
        train.visible = false
        main.visible = true
    }

    function show_train() {
        operation.visible = false
        main.visible = false
        train.visible = true
    }

    function show_operation() {
        train.visible = false
        main.visible = false
        operation.visible = true
    }



    // liste des pages
    UI_main {
        id: main
        objectName: "main"

        anchors.fill: parent

        visible: true
    }

    UI_operation {
        id: operation
        objectName: "operation"

        anchors.fill: parent

        visible: false
    }

    UI_train {
        id: train
        objectName: "train"

        anchors.fill: parent

        visible: false
    }
}
