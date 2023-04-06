import QtQuick 2.15
import QtQuick.Controls 2.15

// Documentation de la personalisation des composants
// https://doc.qt.io/qt-6/qtqml-documents-definetypes.html

// Liste des documentations pour les composants utilisés
// Rectangle :      https://doc.qt.io/qt-6/qml-qtquick-rectangle.html
// Image :          https://doc.qt.io/qt-6/qml-qtquick-image.html
// Text :           https://doc.qt.io/qt-6/qml-qtquick-text.html
// MouseArea :      https://doc.qt.io/qt-6/qml-qtquick-mousearea.html


Item {
    id: root

    // Propriétés liées à l'image et au texte que l'utilisateur peut rajouter sur le bouton
    property int borderWidth: 1             // Taille des bordures du bouton
    property int radius: 0            // Rayon des bordures du bouton
    property string image: ""               // Image à afficher en tout temps sur le bouton si image_enabled et image_disabled sont vides (peut rester vide)
    property string text: ""                // Texte à afficher
    property int fontSize: 12               // Police du texte

    // Propriétés liées à l'état
    property bool enabled: true               // Si le bouton peut être activée

    // Propriétés sur les couleurs utilisées
    property string backgroundColor: "#FFFFFF"
    property string textEnabledColor: "#949494"
    property string textDisabledColor: "#C8C8C8"
    property string highlightColor: "#FFB5FE"

    // Chemin d'accès vers les icones utiles pour le UI_button
    readonly property string symbols_path: "../assets/"

    // Signaux à surchager en QML ou en Python
    signal clicked()                // Appelé lorsque le bouton est relaché
    signal doubleClicked()          // Appelé lorsque le bouton est double cliqué
    signal pressed()                // Appelé lorsque le bouton commenceà être pressé
    signal released()               // Appelé lorsque le bouton est relaché (avec clic valide ou non, clicked sera aussi appelé dans ce second cas)



    // Rectangle pour la couleur du fond du bouton
    Rectangle{
        id: buttonBody

        anchors.fill: parent

        color: root.backgroundColor
        border.width: root.borderWidth
        radius: root.radius
        border.color: root.enabled ? root.textEnabledColor : root.textDisabledColor
    }


    // Image centrée sur le bouton
    Image {
        id: buttonImage

        anchors.top: parent.top
        anchors.topMargin: root.borderWidth
        anchors.left: parent.left
        anchors.leftMargin: root.borderWidth
        anchors.right: parent.right
        anchors.rightMargin: root.borderWidth
        fillMode: Image.PreserveAspectFit

        source: root.image !== "" ? (root.path + root.image)
                                  : ""
    }

    // Texte visible au centre du bouton
    Text{
        id: buttonText

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter

        text: root.text
        font.pixelSize: root.fontSize
        font.family: "Verdana"
        color: root.enabled ? root.textEnabledColor : root.textDisabledColor
    }

    // Zone de détection de souris pour détecter les cliques
    MouseArea{
        id: buttonArea

        anchors.fill: parent

        hoverEnabled: root.enabled
        enabled: root.enabled


        // Répétition des signaux
        onClicked: root.clicked()
        onDoubleClicked: root.doubleClicked()
        onPressed: root.pressed()
        onReleased: root.released()
    }

    // Rectangle pour le highlight
    Rectangle {
        id: buttonHighlight

        anchors.fill: parent
        anchors.margins: buttonBody.border.width
        radius: root.radius

        color: root.highlightColor
        opacity: buttonArea.containsPress ? 0.5 : 0.3
        visible: buttonArea.containsMouse
    }
}
