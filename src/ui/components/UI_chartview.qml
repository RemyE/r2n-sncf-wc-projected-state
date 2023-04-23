import QtQuick 2.15
import QtQuick.Controls 2.15

// https://doc.qt.io/qt-5/qtqml-documents-definetypes.html
// Comment créer un élément personalisé

// https://doc.qt.io/qt-5/qtquickcontrols2-customize.html
// Comment personaliser un composant


Item {
    id: root

    // Propriétés sur les données
    property var datas: []                // Données des SplineSeries. Format: [[[x11, y11], [x12, y12], ...], ...] ou [[[[year11, month11, day11], y11], [[year12, month12, day12], y12], ...], ...]
    property var names: []                // Noms des SplineSeries. Format: ["name", ...]
    property var colors: []               // Couleurs des SplineSeries. Format ["color (hex)", ...]
    property var widths: []               // Epaisseur des traits des SplineSeries. Format [int, int, ...]

    // Propriétés pour l'axe X
    property string xTitle: ""

    property bool xMinimumAuto: false
    onXMinimumAutoChanged: root.updateLimits()
    property double xMinimum: 0.0
    onXMinimumChanged: root.updateLimits()
    readonly property double xDisplayMinimum: xAxis.minimum
    property bool xMaximumAuto: false
    onXMaximumAutoChanged: root.updateLimits()
    property double xMaximum: 0.0
    onXMaximumChanged: root.updateLimits()
    readonly property double xDisplayMaximum: xAxis.maximum
    property int xDecimals: 2

    property int xTicks: 4
    property bool xDateFormat: false
    onXDateFormatChanged: root.updateLimits()

    readonly property int xAxisOrigin: root.x + (root.titleFontSize * (root.xTitle !== "") + 2 * root.fontSize)
    readonly property int xAxisLength: root.width - root.xAxisOrigin + root.x

    // Propriétés pour l'axe Y
    property string yTitle: ""

    property bool yMinimumAuto: false
    onYMinimumAutoChanged: root.updateLimits()
    property double yMinimum: 0.0
    onYMinimumChanged: root.updateLimits()
    readonly property double yDisplayMinimum: yAxis.minimum
    property bool yMaximumAuto: false
    onYMaximumAutoChanged: root.updateLimits()
    property double yMaximum: 0.0
    onYMaximumChanged: root.updateLimits()
    readonly property double yDisplayMaximum: yAxis.maximum
    property int yDecimals: 2

    property int yTicks: 4
    property bool yDateFormat: false
    onYDateFormatChanged: root.updateLimits()

    readonly property int yAxisOrigin: root.y + root.height - (root.titleFontSize * (root.yTitle !== "") + 2 * root.fontSize + 2 * legend.rowsCount * root.fontSize)
    readonly property int yAxisLength: root.yAxisOrigin - root.y

    // Propriétés sur les tailles de textes
    property int fontSize: 12
    property int titleFontSize: root.fontSize * 1.5

    // Propriétés sur les couleurs utilisées
    property string backgroundColor: "#FFFFFF"
    property string textEnabledColor: "#949494"
    property string textDisabledColor: "#C8C8C8"
    property string highlightColor: "#FFB5FE"

    // Fonction pour transformer un nombre au bon format et au bon nombre de décimales en écriture non-scientifique
    function to_string(number, decimals) {
        var fixed = number.toFixed(decimals)                        // Fixe le nombre pour ne pas qu'il soit en notation scientifique
        return fixed.includes(".") ? fixed.replace(/\.?0+$/, "")    // Si le nombre contient un point (décimales)     -> S'assure qu'il n'y a pas de 0 inutiles (12.300 -> 12.3)
                                   : fixed                          // Si le nombre ne contient pas de point (entier) -> Retourne le nombre n'étant pas en écriture scientifique
    }

    // Fonction pour mettre à jour une spline (ou toutes si index invalide)
    // La mise à jour est manuelle car catastrophiquement lente
    function updateValues(spline) {      // Index de 0 à Nsplines - 1
        // Définit les limites des splines à mettre à jour (celle indiquée ou toutes si l'index est invalide)
        // splinesChart.model = root.datas.length ; cependant les composants des Repeater ne sont chargés qu'après chargement complet du composant
        var from = spline >= 0 && spline < charts.count ? spline : 0
        var to = spline >= 0 && spline < charts.count ? spline : charts.count - 1

        // Pour toutes les splines à mettre à jour (toutes, où celle à l'index existant, s'il est valide)
        for (var chartIndex = from ; chartIndex <= to ; chartIndex++) {
            // Demande la mise à jour du Canvas
            charts.itemAt(chartIndex).requestPaint()
        }
    }

    // Fonction pour mettre à jour les valeurs limites des axes du graphique
    function updateLimits() {
        // Redéfinit les valeurs minimales et maximales de l'axe x
        // Trouve la valeur minimale et maximale, en récupérant toutes les valeurs et en les comparants
        var values = []
        for (var splineIndex=0 ; splineIndex < root.datas.length ; splineIndex++) {
            for (var pointIndex=0 ; pointIndex < root.datas[splineIndex].length ; pointIndex++) {
                values.push(root.datas[splineIndex][pointIndex][0])
            }
        }
        if (values.length > 0 || !root.xDateFormat) {
            // Si la limite xMinimum doit être changée automatiquement, le change
            if (root.xMinimumAuto) {
                var xMin =  values.reduce(function (previous, current) {
                    return previous > current ? current : previous;
                }, Math.max(root.xMaximum, root.xMinimum));
                xAxis.minimum = xMin > root.xMinimum ? xMin : root.xMinimum
            }
            else {
                xAxis.minimum = root.xMinimum
            }

            // Si la limite xMaximum doit être changée automatiquement, le change
            if (root.xMaximumAuto) {
                var xMax = values.reduce(function (previous, current) {
                    return previous < current ? current : previous;
                }, Math.min(root.xMinimum, root.xMaximum));
                xAxis.maximum = xMax < root.xMaximum ? xMax : root.xMaximum
            }
            else {
                xAxis.maximum = root.xMaximum
            }
        }
        else {
            // Si la limite xMinimum doit être changée automatiquement, le change
            if (root.xMinimumAuto) {
                xAxis.minimum = parseInt(Date.parse(new Date()) / (24 * 60 * 60 * 1000)) * (24 * 60 * 60 * 1000)
            }
            else {
                xAxis.minimum = root.xMinimum
            }

            // Si la limite xMaximum doit être changée automatiquement, le change
            if (root.xMaximumAuto) {
                xAxis.maximum = parseInt(Date.parse(new Date()) / (24 * 60 * 60 * 1000)) * (24 * 60 * 60 * 1000)
            }
            else {
                xAxis.maximum = root.xMaximum
            }
        }

        // Redéfinit la valeur maximale de l'axe y (la valeur minimale sera toujours de 0
        // Trouve la valeur minimale et maximale, en récupérant toutes les valeurs et en les comparants
        var values = []
        for (var splineIndex=0 ; splineIndex < root.datas.length ; splineIndex++) {
            for (var pointIndex=0 ; pointIndex < root.datas[splineIndex].length ; pointIndex++) {
                values.push(root.datas[splineIndex][pointIndex][1])
            }
        }

        // Si la limite yMinimum doit être changée automatiquement, le change
        if (root.yMinimumAuto) {
            var yMin = values.reduce(function (previous, current) {
                return previous > current ? current : previous;
            }, Math.max(root.yMaximum, root.yMinimum));
            yAxis.minimum = yMin > root.yMinimum ? yMin : root.yMinimum
        }
        else {
            yAxis.maximum = root.yMaximum
        }

        // Si la limite yMaximum doit être changée automatiquement, le change
        if (root.yMaximumAuto) {
            var yMax = values.reduce(function (previous, current) {
                return previous < current ? current : previous;
            }, Math.min(root.yMinimum, root.yMaximum));
            yAxis.maximum = yMax < root.yMaximum ? yMax : root.yMaximum
        }
        else {
            yAxis.maximum = root.yMaximum
        }
    }

    // Détecte lorsque la liste des splines est mise à jour, ajoute un delai avant l'appel et met à jour les limites et les valeurs
    onDatasChanged: delayTimer.start()

    Timer {
        id: delayTimer

        interval: 5; repeat: false
        onTriggered: {
            // Redéfinit les valeurs limites des graphiques
            root.updateLimits()

            // Passe sur chacune des bars et la met à jour
            for (var chartIndex=0 ; chartIndex < charts.count ; chartIndex++) {
                root.updateValues(chartIndex)
            }
        }
    }


    // Axe X
    Repeater {
        id: xAxis

        anchors.fill: parent

        // Propriétés sur les valeurs limites
        property double minimum: 0.0
        property double maximum: 0.0

        model: Math.max(root.xTicks, 2)


        // Rectangle de démarcation de la ligne
        Rectangle {
            id: xLabelsMarker

            // Index du marqueur pour l'utiliser dans les propriétés des enfants
            readonly property int markerIndex: index

            x: root.xAxisOrigin - root.x + (root.xAxisLength * markerIndex / (Math.max(root.xTicks, 2) - 1))
            y: root.yAxisOrigin - root.y - root.yAxisLength
            width: 1 + (markerIndex === 0)
            height: root.yAxisLength

            color: markerIndex === 0 ? root.textEnabledColor : root.textDisabledColor



            // Valeur à afficher
            Text {
                id: xLabelsText

                // Propriété sur la valeur numérique de l'axe (pour simplifier la lecture
                readonly property double numeric_value: xAxis.minimum + ((xAxis.maximum - xAxis.minimum) * parent.markerIndex / (Math.max(root.xTicks, 2) - 1))

                anchors.top: parent.bottom
                anchors.topMargin: root.fontSize / 2
                anchors.horizontalCenter: parent.horizontalCenter

                text: root.xDateFormat ? `${(new Date(numeric_value)).getUTCDate()}-${(new Date(numeric_value)).getUTCMonth() + 1}-${(new Date(numeric_value)).getUTCFullYear()}`
                                           : root.to_string(numeric_value, root.xDecimals).toString()
                color: root.textEnabledColor
                font.family: "Verdana"
                font.pixelSize: root.fontSize

                TextMetrics {
                    id: xLabelsMetrics

                    font: xLabelsText.font
                    text: xLabelsText.text
                }
            }
        }
    }

    // Titre de l'axe X
    Text {
       id: xTitleText

        x: root.xAxisOrigin - root.x + (root.xAxisLength - xTitleMetrics.boundingRect.width) / 2
        y: root.yAxisOrigin - root.y + 2 * root.fontSize

        text: root.xTitle
        color: root.textEnabledColor
        font.family: "Verdana"
        font.pixelSize: root.titleFontSize

        TextMetrics {
            id: xTitleMetrics

            font: xTitleText.font
            text: xTitleText.text
        }
    }


    // Axe Y
    Repeater {
        id: yAxis

        anchors.fill: parent

        // Propriétés sur les valeurs limites
        property double minimum: 0.0
        property double maximum: 0.0

        model: Math.max(root.yTicks, 2)



        // Rectangle de démarcation de la ligne
        Rectangle {
            id: yLabelsMarker

            // Index du marqueur pour l'utiliser dans les propriétés des enfants
            readonly property int markerIndex: index

            x: root.xAxisOrigin - root.x
            y: root.yAxisOrigin - root.y - (root.yAxisLength * markerIndex / (Math.max(root.yTicks, 2) - 1))
            width: root.xAxisLength
            height: 1 + (markerIndex === 0)

            color: markerIndex === 0 ? root.textEnabledColor : root.textDisabledColor



            // Valeur à afficher
            Text {
                id: yLabelsText

                // Propriété sur la valeur numérique de l'axe (pour simplifier la lecture
                readonly property double numeric_value: yAxis.minimum + ((yAxis.maximum - yAxis.minimum) * parent.markerIndex / (Math.max(root.yTicks, 2) - 1))

                x: - root.fontSize * 3/2
                y: + yLabelsMetrics.tightBoundingRect.width

                text: root.yDateFormat ? `${(new Date(numeric_value)).getUTCDate()}-${(new Date(numeric_value)).getUTCMonth() + 1}-${(new Date(numeric_value)).getUTCFullYear()}`
                                           : root.to_string(numeric_value, root.yDecimals)
                transform: Rotation { origin.x: 0; origin.y: 0; angle: -90; }
                color: root.textEnabledColor
                font.family: "Verdana"
                font.pixelSize: root.fontSize

                TextMetrics {
                    id: yLabelsMetrics

                    font: yLabelsText.font
                    text: yLabelsText.text
                }
            }
        }
    }

    // Titre de l'axe Y
    Text {
       id: yTitleText

        x: root.xAxisOrigin - root.x - 2 * root.fontSize - root.titleFontSize
        y: root.yAxisOrigin - root.y - (root.yAxisLength - yTitleMetrics.boundingRect.width) / 2

        text: root.yTitle
        transform: Rotation { origin.x: 0; origin.y: 0; angle: -90; }
        color: root.textEnabledColor
        font.family: "Verdana"
        font.pixelSize: root.titleFontSize

        TextMetrics {
            id: yTitleMetrics

            font: yTitleText.font
            text: yTitleText.text
        }
    }

    // Repeater pour afficher toutes les splines
    Repeater {
        id: charts

        anchors.fill: parent

        // Autant de graphiques qu'il y a de courbes à afficher
        model: Math.min(root.datas.length, root.names.length, root.colors.length, root.widths.length)

        Canvas {
            id: chart

            // Propriété sur l'index du graphique
            readonly property int chartIndex: index

            x: root.xAxisOrigin - root.x
            y: root.yAxisOrigin - root.y - root.yAxisLength
            width: root.xAxisLength
            height: root.yAxisLength

            onPaint: {
                var ctx = getContext("2d");
                ctx.reset();
                ctx.beginPath();

                // Défini l'épaisseur et la couleur de remplissage de la ligne
                ctx.lineWidth = root.widths[chartIndex];
                ctx.lineCap = "round";
                ctx.strokeStyle = root.colors[chartIndex]

                // Dessine toutes les sections de lignes
                if (root.datas[chartIndex].length > 0) {
                    ctx.moveTo(root.xAxisLength * (root.datas[chartIndex][0][0] - xAxis.minimum) / Math.max((xAxis.maximum - xAxis.minimum), 1),     // Math.min pour éviter les divisions par 0 si aucune valeur
                               root.yAxisLength - (root.yAxisLength * (root.datas[chartIndex][0][1] - yAxis.minimum) / Math.max((yAxis.maximum - yAxis.minimum), 1)))
                }
                for (var pointIndex = 1 ; pointIndex < root.datas[chartIndex].length ; pointIndex++) {
                    ctx.lineTo(root.xAxisLength * (root.datas[chartIndex][pointIndex][0] - xAxis.minimum) / Math.max((xAxis.maximum - xAxis.minimum), 1),
                               root.yAxisLength - (root.yAxisLength * (root.datas[chartIndex][pointIndex][1] - yAxis.minimum) / Math.max((yAxis.maximum - yAxis.minimum), 1)))
                }

                // Ferme le chemin
                ctx.stroke();
            }
        }

    }

    // Fais une première update de toutes les splines pour les montrer une fois le composant chargé
    Component.onCompleted: {root.updateLimits(); root.updateValues(-1) }


    Repeater {
        id: legend

        // Propriétés sur les dimensions de la légende
        property int longestLegendLength: 0
        readonly property int columnsCount: Math.max(root.xAxisLength / parseInt(legend.longestLegendLength + 4 * root.fontSize), 1)
        readonly property int rowsCount: Math.max(parseInt(0.99 + (legend.count / legend.columnsCount)), 0)

        model: Math.min(root.names.length, root.colors.length)


        // Signal appelé lorsque le nombre d'éléments change
        onCountChanged: {
            // Passe sur chacun des textes et récupère la longueur du texte le plus long et l'indique
            var longest = 0
            for (var legendIndex = 0 ; legendIndex < legend.count ; legendIndex++) {
                longest = longest > legend.itemAt(legendIndex).textWidth ? longest : legend.itemAt(legendIndex).textWidth
            }
            legend.longestLegendLength = longest
        }

        Item {
            // Propriété sur la largeur du texte de la légende
            readonly property int textWidth: legendMetrics.tightBoundingRect.width

            Rectangle {
                x: root.xAxisOrigin + (legend.longestLegendLength + 4 * root.fontSize) * (index % legend.columnsCount)
                y: root.yAxisOrigin + 2 * root.fontSize * (1.5 + parseInt(index / legend.columnsCount))
                width: root.fontSize
                height: root.fontSize

                color: root.colors[index]
                border.width: 1
                border.color: root.textEnabledColor
            }

            Text {
                id: legendText

                x: root.xAxisOrigin + 2 * root.fontSize + (legend.longestLegendLength + 4 * root.fontSize) * (index % legend.columnsCount)
                y: root.yAxisOrigin + 2 * root.fontSize * (1.5 + parseInt(index / legend.columnsCount))
                width: root.fontSize
                height: root.fontSize

                text: root.names[index]
                color: index < root.datas.length ? root.textEnabledColor : root.textDisabledColor



                TextMetrics {
                    id: legendMetrics

                    font: legendText.font
                    text: legendText.text
                }
            }
        }
    }
}
