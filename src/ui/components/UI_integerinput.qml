import QtQuick 2.15
import QtQuick.Controls 2.15

// https://doc.qt.io/qt-5/qtqml-documents-definetypes.html
// Comment créer un élément personalisé

// https://doc.qt.io/qt-5/qtquickcontrols2-customize.html
// Comment personaliser un composant


Item {
    id: root

    // Propriétés sur les valeurs limites
    property int minimum: 0
    property int maximum: 1
    property bool defaultMaximum: true
    property string placeholderText: ""
    readonly property int value: body.displayText === "" ? (root.defaultMaximum ? body.validator.top : body.validator.bottom) : parseInt(body.displayText)


    // Fonction pour changer la valeur du textfield
    function change_value(new_value){
        // Cas où la valeur n'est pas valide (trop grand ou trop petite)
        if(new_value < body.validator.bottom || new_value > body.validator.top) {
            // L'indique dans le registre et change la valeur pour qu'elle rentre dans les bornes
            new_value = new_value < body.validator.bottom ? body.validator.bottom
                                                          : body.validator.top

        }

        // Si la nouvelle valeur est différente de l'actuelle, change la valeur, appelle le signal value_changed
        if(root.value !== new_value){
            body.text = new_value
        }
    }


    TextField {
        id: body

        anchors.fill: parent

        horizontalAlignment: Qt.AlignHCenter
        verticalAlignment: Qt.AlignVCenter

        placeholderText: root.placeholderText
        validator: IntValidator {bottom: Math.max(root.minimum, 0); top: Math.max(root.minimum, root.maximum, 0);}
    }
}