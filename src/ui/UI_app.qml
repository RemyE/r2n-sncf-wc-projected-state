import QtQuick
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "components/"
import "graphic/"

// Fenêtre principale de l'application
Window {
    id: window
    minimumWidth: 960
    minimumHeight: 540
    title: "SNCF-toilet-data-analyser"
    color: window.backgroundColor

    // Propriété pour définir la couleur d'arrière-plan de la fenêtre
    property string backgroundColor: "#FFFFFF"

    // Fonctions pour naviguer entre les pages

    // Affiche la page principale et cache les autres
    function go_back() {
        operation.visible = false
        prediction.visible = false
        main.visible = true
    }

    // Affiche la page de prédiction et cache les autres
    function show_prediction() {
        operation.visible = false
        main.visible = false
        prediction.visible = true
    }

    // Affiche la page des opérations et cache les autres
    function show_operation() {
        prediction.visible = false
        main.visible = false
        operation.visible = true
    }

    // Liste des pages de l'application

    // Page principale
    UI_main {
        id: main
        objectName: "main"

        anchors.fill: parent

        visible: true
    }

    // Page des opérations
    UI_operation {
        id: operation
        objectName: "operation"

        anchors.fill: parent

        visible: false
    }

    // Page des prédictions
    UI_prediction {
        id: prediction
        objectName: "prediction"

        anchors.fill: parent

        visible: false
    }
}
