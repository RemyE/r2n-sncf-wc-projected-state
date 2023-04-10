import QtQuick
import QtQuick.Controls

// Documentation de la personalisation des composants
// https://doc.qt.io/qt-6/qtqml-documents-definetypes.html

// Liste des documentations pour les composants utilisés
// Rectangle :      https://doc.qt.io/qt-6/qml-qtquick-rectangle.html
// Image :          https://doc.qt.io/qt-6/qml-qtquick-image.html
// Text :           https://doc.qt.io/qt-6/qml-qtquick-text.html
// MouseArea :      https://doc.qt.io/qt-6/qml-qtquick-mousearea.html


Item {
    id: root

    // Propriétés liées à la sélection et au texte
    property string title: ""
    property var elements: []
    property int fontSize: 12
    readonly property string selection: operationCombobox.displayText
    onSelectionChanged: root.changed()

    // Propriétés sur l'étatdu composant
    property bool enabled: true
    property bool add: true

    // Propriétés sur les couleurs utilisées
    property string backgroundColor: "#FFFFFF"
    property string textEnabledColor: "#949494"
    property string textDisabledColor: "#C8C8C8"
    property string highlightColor: "#FFB5FE"


    // Signaux à surcharger en QML ou en Python
    signal leftAdd()    // Appelé lorsque le bouton pour ajouter une opération à gauche est cliqué
    signal rightAdd()   // Appelé lorsque le bouton pour ajouter une opération à droite est cliqué
    signal removed()     // Appelé lorsque le bouton pour cliquer
    signal changed()    // Appelé lorsque la sélection du combobox a changé


    // Fonction permettant de réinitialiser la sélection
    function reset() {
        operationCombobox.currentIndex = 0
    }

    // Fonction permettant de changer l'index actif
    function changeSelection(newSelection) {
        // Cas où la nouvelle sélection est fourni en tant que texte, récupère l'index à partir du texte
        if (typeof newSelection !== "number") {
            newSelection = root.elements.indexOf(newSelection) + 1
        }

        // Cas où la sélection est un nombre valide, la change
        if (operationCombobox.count > 0 && 0 <= newSelection && newSelection < operationCombobox.count) {
            operationCombobox.currentIndex = newSelection
        }
    }


    // Texte pour afficher l'index de l'opération
    Text {
        id: operationText

        x: root.fontSize
        y: root.fontSize / 2

        text: root.title
        font.pixelSize: root.fontSize
        font.family: "Verdana"
        color: root.selection === "" ? root.textDisabledColor : root.textEnabledColor
    }

    // Bouton pour supprimer l'opération
    UI_button {
        id: removeButton

        x: root.width - 3 * root.fontSize + 2
        y: root.y + 2
        width: 2 * root.fontSize - 4
        height: width
        radius: height / 2
        borderWidth: 1

        text: "x"
        fontSize: root.fontSize

        onClicked: root.removed()
    }

    // Combobox pour la sélection de l'opération
    ComboBox {
        id: operationCombobox

        x: root.fontSize
        y: 2 * root.fontSize
        width: root.width - 2 * root.fontSize
        height: root.height - 2 * root.fontSize - 2

        model: [""].concat(root.elements)       // Ajoute un élément vide pour laisser l'utilisateur choisir

        delegate: ItemDelegate {
            width: operationCombobox.width
            contentItem: Text {
                text: operationCombobox.textRole
                    ? (Array.isArray(operationCombobox.model) ? modelData[operationCombobox.textRole] : model[operationCombobox.textRole])
                    : modelData
                color: root.textEnabledColor
                font.pixelSize: root.fontSize
                font.family: "Verdana"
                elide: Text.ElideRight
                verticalAlignment: Text.AlignVCenter
            }
            highlighted: operationCombobox.highlightedIndex === index
        }

        indicator: Canvas {
            id: canvas
            x: operationCombobox.width - width - operationCombobox.rightPadding
            y: operationCombobox.topPadding + (operationCombobox.availableHeight - height) / 2
            width: 12
            height: 8
            contextType: "2d"

            Connections {
                target: operationCombobox
                function onPressedChanged() { canvas.requestPaint(); }
            }

            onPaint: {
                context.reset();
                context.moveTo(0, 0);
                context.lineTo(width, 0);
                context.lineTo(width / 2, height);
                context.closePath();
                context.fillStyle = operationCombobox.pressed ? root.textDisabledColor : root.textEnabledColor;
                context.fill();
            }
        }

        contentItem: Text {
            leftPadding: 0
            rightPadding: operationCombobox.indicator.width + operationCombobox.spacing

            text: operationCombobox.displayText
            font: operationCombobox.font
            color: operationCombobox.pressed ?  root.textDisabledColor : root.textEnabledColor
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }

        background: Rectangle {
            implicitWidth: 120
            implicitHeight: 40
            color: root.backgroundColor
            border.color: operationCombobox.pressed ? root.textDisabledColor : root.textEnabledColor
            border.width: 1
            radius: 0
        }

        popup: Popup {
            y: operationCombobox.height - 1
            width: operationCombobox.width
            implicitHeight: contentItem.implicitHeight
            padding: 1

            contentItem: ListView {
                clip: true
                implicitHeight: contentHeight
                model: operationCombobox.popup.visible ? operationCombobox.delegateModel : null
                currentIndex: operationCombobox.highlightedIndex

                ScrollIndicator.vertical: ScrollIndicator { }
            }

            background: Rectangle {
                color: root.backgroundColor
                border.color: root.textEnabledColor
                border.width: 1
                radius: 0
            }
        }
    }


    // Zones de détection
    MouseArea {
        id: leftAddArea

        anchors.top: operationCombobox.top
        anchors.bottom: operationCombobox.bottom
        anchors.right: operationCombobox.left
        width: root.fontSize

        enabled: true //root.add && root.enabled
        hoverEnabled: true //root.add && root.enabled


        Text {
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.left

            text: "+"
            font.pixelSize: root.fontSize
            font.family: "Verdana"
            color: root.textEnabledColor

            visible: leftAddArea.containsMouse
        }


        // Répète le signal de clic
        onReleased: root.leftAdd()
    }

    MouseArea {
        id: rightAddArea

        anchors.top: operationCombobox.top
        anchors.bottom: operationCombobox.bottom
        anchors.left: operationCombobox.right
        width: root.fontSize

        enabled: true //root.add && root.enabled
        hoverEnabled: true //root.add && root.enabled


        Text {
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.right

            text: "+"
            font.pixelSize: root.fontSize
            font.family: "Verdana"
            color: root.textEnabledColor

            visible: rightAddArea.containsMouse
        }


        // Répète le signal de clic
        onReleased: root.rightAdd()
    }


    // TODO : ajouter le surlignage
}
