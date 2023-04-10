import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"


Item {
    id: root

    // Propriété sur la validité des valeurs
    readonly property bool valid: root.cleanWaterData.length !== 0 && root.poopooWaterData.length !== 0

    // Propriété sur les valeurs
    property var operations: []                     // Liste des opérations ayant des données. Défini à l'initialisation
    property var selections: [""]                   // liste des sélections de operations
    onSelectionsChanged: root.dataChanged()
    readonly property int defaultCleanWaterBaseLevel: 135
    readonly property int cleanWaterBaseLevel: cleanInput.value   // Remplissage par défaut du réservoir d'eau propre
    onCleanWaterBaseLevelChanged: root.updateValues()
    property int cleanWaterWarningIndex: 0          // Index à partir duquel le niveau de réservoir d'eau claire est problématique ou critique
    property int cleanWaterCriticalIndex: 0
    property int defaultPoopooWaterBaseLevel: 315.0 // Remplissage limite du réservoir d'eau sale
    property int poopooWaterBaseLevel: poopooInput.value          // Remplissage limite du réservoir d'eau sale
    onPoopooWaterBaseLevelChanged: root.updateValues()
    property int poopooWaterWarningIndex: 0         // Index à partir duquel le niveau du réservoir d'eau sale est problématique ou critique
    property int poopooWaterCriticalIndex: 0
    property var names: ["opération 1"]             // Liste des noms des opérations
    property var cleanWaterData: []                 // format [[min, avg, max], ...]
    property var cumCleanWaterData: []              // format [[min, avg, max], ...] -> Format SplineSeries
    property var poopooWaterData: []                // format [[min, avg, max], ...]
    property var cumPoopooWaterData: []             // format [[min, avg, max], ...] -> Format SplineSeries

    // Signaux à redéfinir en QML ou en Python
    signal dataChanged()            // Appelé lorsqu'une sélection a été modifiée, ajoutée ou supprimée


    // Fonction de réinitialisation du module
    function reset() {
        // Réinitialise la liste des opérations et des noms, appelle automatiquement le signal dataChanged()
        root.names = ["opération 1"]
        root.selections = [""]
    }

    // Fonction de mise à jour des graphiques, à appeler dès que les données changent où qu'une marche est ajoutée/supprimée
    function updateValues() {
        // Initialise la liste des valeurs cumulatives, en commançant au niveau max pour les eaux clairs et y ajoute toutes les valeurs cumulées
        // Attention! Ici on compte (on pars d'un réservoir plein que l'on vide)
        var cleanCumData = [[root.cleanWaterBaseLevel, root.cleanWaterBaseLevel, root.cleanWaterBaseLevel]]
        for (var operationIndex = 0 ; operationIndex < root.cleanWaterData.length ; operationIndex++) {
            cleanCumData.push([Math.max(cleanCumData[operationIndex][0] - root.cleanWaterData[operationIndex][0], 0),
                               Math.max(cleanCumData[operationIndex][1] - root.cleanWaterData[operationIndex][1], 0),
                               Math.max(cleanCumData[operationIndex][2] - root.cleanWaterData[operationIndex][2], 0)])

            // Si le nouveau niveau minimum ou moyen dépasse le seuil, indique l'index de criticité
            if (cleanCumData[operationIndex + 1][2] === 0 && cleanCumData[operationIndex][2] !== 0) {
                root.cleanWaterWarningIndex = operationIndex
            }
            if (cleanCumData[operationIndex + 1][1] === 0 && cleanCumData[operationIndex][1] !== 0) {
                root.cleanWaterCriticalIndex = operationIndex
            }
        }

        // Si les seuils de criticité n'ont pas été dépassés, les définis au nombre de operation
        if (cleanCumData[cleanCumData.length - 1][2] !== 0) {
            root.cleanWaterWarningIndex = cleanCumData.length
        }
        if (cleanCumData[cleanCumData.length - 1][1] !== 0) {
            root.cleanWaterCriticalIndex = cleanCumData.length
        }

        // Défini la liste des valeurs visible par l'utilisateur et le graphe
        root.cumCleanWaterData = cleanCumData

        // Réitère le même procédé avec les valeurs d'eau sale
        // Initialise la liste des valeurs cumulatives, en commançant au niveau max pour les eaux clairs et y ajoute toutes les valeurs cumulées
        // Attention! Ici, on décompte (on pars d'un réservoir vide que l'on rempli)
        var poopooCumData = [[0, 0, 0]]
        for (var operationIndex = 0 ; operationIndex < root.poopooWaterData.length ; operationIndex++) {
            poopooCumData.push([Math.min(poopooCumData[operationIndex][0] + root.poopooWaterData[operationIndex][0], root.poopooWaterBaseLevel),
                                Math.min(poopooCumData[operationIndex][1] + root.poopooWaterData[operationIndex][1], root.poopooWaterBaseLevel),
                                Math.min(poopooCumData[operationIndex][2] + root.poopooWaterData[operationIndex][2], root.poopooWaterBaseLevel)])

            // Si le nouveau niveau minimum ou moyen dépasse le seuil, indique l'index de criticité
            if (poopooCumData[operationIndex + 1][2] === root.poopooWaterBaseLevel && poopooCumData[operationIndex][2] !== root.poopooWaterBaseLevel) {
                root.poopooWaterWarningIndex = operationIndex
            }
            if (cleanCumData[operationIndex + 1][1] === root.poopooWaterBaseLevel && cleanCumData[operationIndex][1] !== root.poopooWaterBaseLevel) {
                root.poopooWaterCriticalIndex = operationIndex
            }
        }

        // Si les seuils de criticité n'ont pas été dépassés, les définis au nombre de operation
        if (cleanCumData[cleanCumData.length - 1][2] !== root.poopooWaterBaseLevel) {
            root.poopooWaterWarningIndex = poopooCumData.length
        }
        if (cleanCumData[cleanCumData.length - 1][1] !== root.poopooWaterBaseLevel) {
            root.poopooWaterCriticalIndex = poopooCumData.length
        }

        // Défini la liste des valeurs visible par l'utilisateur et le graphe
        root.cumPoopooWaterData = poopooCumData

        // Reconvertit toutes les valeurs, cette fois pour les envoyées au chartView
        // Commence par les données sur l'eau claire
        var datas = []
        for (var splineIndex=0 ; splineIndex < (root.cumCleanWaterData.length > 0 ? root.cumCleanWaterData[0].length : 0) ; splineIndex++) {
            // Ajoute une liste avec les points et rajoute chacun des points
            datas.push([])
            for (var pointIndex=0 ; pointIndex < root.cumCleanWaterData.length ; pointIndex++) {
                datas[datas.length - 1].push([pointIndex, root.cumCleanWaterData[pointIndex][splineIndex]])
            }
        }

        // Ajoute les données sur l'eau sale
        for (var splineIndex=0 ; splineIndex < (root.cumPoopooWaterData.length > 0 ? root.cumPoopooWaterData[0].length : 0) ; splineIndex++) {
            // Ajoute une liste avec les points et rajoute chacun des points
            datas.push([])
            for (var pointIndex=0 ; pointIndex < root.cumPoopooWaterData.length ; pointIndex++) {
                datas[datas.length - 1].push([pointIndex, root.cumPoopooWaterData[pointIndex][splineIndex]])
            }
        }
        predictionChart.datas = datas

        // Lance le chronomètre pour mettre à jour l'affichage et correctement mettre à jour la liste des opérations effectuées
        delayTimer.start()
    }

    // Fonction de mise à jour du composant de sélection
    function updateOperations() {
        // Repasse sur la liste de chacune des opérations, pour correctement afficher leur sélection
        for (var operationIndex = 0 ; operationIndex < selectorView.count ; operationIndex++) {
            selectorView.currentIndex = operationIndex
            selectorView.currentItem.changeSelection(root.selections[operationIndex])
        }
    }

    Timer {
        id: delayTimer

        interval: 5; repeat: false
        onTriggered: root.updateOperations()
    }



    // Bouton de retour
    UI_button {
        id: returnButton
        objectName: "returnButton"
        
        anchors.top: parent.top
        anchors.topMargin: 8
        anchors.left: parent.left
        anchors.leftMargin : 8
        width: 100
        height: 30
        
        text: "retour"
    }
    
    // Titre
    Text {
        id: title
        
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: returnButton.verticalCenter
        
        text: "Outil de prédiction"
        color: root.valid ? returnButton.textEnabledColor : returnButton.textDisabledColor
        
    }
    
    // Bouton de sauvegarde
    UI_button {
        id: saveButton
        objectName: "saveButton"
        
        anchors.top: parent.top
        anchors.topMargin: returnButton.anchors.topMargin
        anchors.right: parent.right
        anchors.rightMargin: returnButton.anchors.leftMargin
        width: returnButton.width
        height: returnButton.height

        text: "sauvegarder"
    }


    // Rectangle pour les entrées de valeurs
    Rectangle {
        id: baseBody

        anchors.top:  returnButton.bottom
        anchors.topMargin: returnButton.anchors.topMargin
        anchors.left: returnButton.left
        width: 150
        z: selectorBody.z + 1           // Met le composant au dessus de l'onglet de sélection pour ne pas être caché par les opérations

        height: returnButton.height * 2 + 20
        border.width: 3 * returnButton.borderWidth

        color: returnButton.backgroundColor
        border.color: returnButton.textEnabledColor


        UI_integerinput {
            id: cleanInput

            anchors.left: parent.left
            anchors.leftMargin: parent.border.width
            anchors.right: parent.right
            anchors.rightMargin: parent.border.width
            anchors.top: parent.top
            anchors.topMargin: parent.border.width
            anchors.bottom: parent.verticalCenter

            placeholderText: "Limite réservoir eau propre"

            minimum: 0
            maximum: 1000
            Component.onCompleted: cleanInput.change_value(root.defaultCleanWaterBaseLevel)
        }

        UI_integerinput {
            id: poopooInput

            anchors.left: parent.left
            anchors.leftMargin: parent.border.width
            anchors.right: parent.right
            anchors.rightMargin: parent.border.width
            anchors.top: parent.verticalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: parent.border.width

            placeholderText: "Limite réservoir eau sale"

            minimum: 0
            maximum: 1000
            Component.onCompleted: poopooInput.change_value(root.defaultPoopooWaterBaseLevel)
        }
    }

    // Rectangle pour la structure de visualisation, de sélection et d'ajout des operations
    Rectangle {
        id: selectorBody

        anchors.top:  returnButton.bottom
        anchors.topMargin: returnButton.anchors.topMargin
        anchors.left: baseBody.right
        anchors.right: saveButton.right
        height: returnButton.height * 2 + 20
        border.width: 3 * returnButton.borderWidth

        color: returnButton.backgroundColor
        border.color: returnButton.textEnabledColor



        ListView {
            id: selectorView

            anchors.left: parent.left
            anchors.leftMargin: 2
            anchors.right: parent.right
            anchors.rightMargin: 2
            anchors.top: parent.top
            anchors.topMargin: 2
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 2

            orientation: Qt.Horizontal

            model: Math.min(root.names.length, root.operations.length)

            delegate: UI_operation_selector {
                anchors.top: parent ? parent.top : undefined
                anchors.bottom: parent ? parent.bottom : undefined
                anchors.bottomMargin: 20
                width: 240

                title: root.names[index]
                elements: root.operations

                critical: [root.cleanWaterCriticalIndex <= index,
                           root.poopooWaterCriticalIndex <= index]
                warning: [root.cleanWaterWarningIndex <= index,
                          root.poopooWaterWarningIndex <= index]

                enabled: root.valid
                add: root.valid


                // Appelé lorque l'élément est enlevé
                onRemoved: {
                    // Cas, il reste un seul élément, le réinitialise
                    if(selectorView.count === 1) {
                        // Changer la sélection appelera potentiellement le signal change()
                        reset()
                    }
                    // Cas, il reste plus d'un élément, l'enlève
                    else {
                        // Enlever des éléments des listes appelera automatiquement le signal dataChanged()
                        root.names.splice(root.names.length - 1, 1) // ici le dernier nom est enlever pour garder une continuité sur les index
                        root.selections.splice(index, 1)
                        root.selectionsChanged()
                        root.namesChanged()
                    }
                }

                // Appelé lorsque l'élément est changé
                onChanged: {
                    // Met à jour l'information uniquement si la sélection change (pour éviter une boucle infin)
                    if (root.selections[index] !== index) {
                        // Change la sélection pour la nouvelle sélection et appelle manuellement le signal
                        root.selections[index] = selection
                        root.selectionsChanged()
                    }
                }

                // Appelé lorsque un élément est ajouté à droite
                onLeftAdd: {
                    // Ajoute un élément dans la liste ce qui appelera automatiquement le signal dataChanged()
                    root.names.splice(root.names.length, 0, `opération ${root.names.length + 1}`) // ici le dernier nom est enlever pour garder une continuité sur les index
                    root.selections.splice(index, 0, "")
                    root.selectionsChanged()
                    root.namesChanged()
                }

                onRightAdd: {
                    // Ajoute un élément dans la liste ce qui appelera automatiquement le signal dataChanged()
                    root.names.splice(root.names.length, 0, `opération ${root.names.length + 1}`) // ici le dernier nom est enlever pour garder une continuité sur les index
                    root.selections.splice(index + 1, 0, "")
                    root.selectionsChanged()
                    root.namesChanged()
                }
            }

            ScrollBar.horizontal: ScrollBar {}
        }
    }


    // Rectangle pour la structure de visualisation, de sélection et d'ajout des missions
    Rectangle {
        id: predictionBody

        anchors.top:  selectorBody.bottom
        anchors.topMargin: selectorBody.anchors.topMargin
        anchors.left: returnButton.left
        anchors.right: saveButton.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: returnButton.anchors.topMargin
        border.width: 3 * returnButton.borderWidth

        color: returnButton.backgroundColor
        border.color: returnButton.textEnabledColor

        // TODO : ajouter le UI_chartview
    }
}