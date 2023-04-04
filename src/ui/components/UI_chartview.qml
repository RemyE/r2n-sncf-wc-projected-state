import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.3

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
    readonly property bool dateFormat: datas.length > 0 && datas[0].length > 0 && isNaN(datas[0][0][0])

    // Propriétés sur les axes (axes communs pour x et séparés pour y)
    property string xTitle: ""
    property int xDecimals: 2
    property int xTicks: 4
    property int xMinorTicks: 0
    property string yTitle: ""
    property int yDecimals: 2
    property int yTicks: 4
    property int yMinorTicks: 0
    // Les valeurs limites sur chaque axes sont définis selon la valeur maximale pour toujours afficher un maximum de données

    // Propriétés sur les tailles de textes
    property int fontSize: 12
    property int titleFontSize: root.fontSize * 1.5

    // Propriétés sur les couleurs utilisées
    property string backgroundColor: "#000000"
    property string textEnabledColor: "#C8C8C8"
    property string textDisabledColor: "#939393"
    property string highlightColor: "#000080"

    // Fonction pour transformer un nombre au bon format et au bon nombre de décimales en écriture non-scientifique
    function toString(number, decimals) {
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
            // Réinitialise la spline
            charts.itemAt(chartIndex).clear()

            // Rajoute tous les nouveaux points
            for (var pointIndex = 0 ; pointIndex < root.datas[chartIndex].length ; pointIndex++) {
                charts.itemAt(chartIndex).addPoint(root.datas[chartIndex][pointIndex][0],
                                                   root.datas[chartIndex][pointIndex][1])
            }
        }
    }

    // Fonction pour mettre à jour les valeurs limites des axes du graphique
    function updateLimits() {
        // Redéfinit les valeurs minimales et maximales de l'axe x
        // Différencie le cas d'une date ou d'un nombre pour la valeur x
        if (root.dateFormat) {
            // Trouve la date minimale et maximale, en récupérant toutes les dates et en les comparants
            var dates = []
            for (var splineIndex=0 ; splineIndex < root.datas.length ; splineIndex++) {
                for (var pointIndex=0 ; pointIndex < root.datas[splineIndex].length ; pointIndex++) {
                    dates.append(root.datas[splineIndex][pointIndex][0])
                }
            }
            var earliest = dates.reduce(function (previous, current) {
                return Date.parse(previous) > Date.parse(current) ? current : previous;
            }, [(new Date()).getUTCFullYear(), (new Date()).getUTCMonth() + 1, (new Date()).getUTCDate()]);
            var newest = dates.reduce(function (previous, current) {
                return Date.parse(previous) < Date.parse(current) ? current : previous;
            }, [(new Date()).getUTCFullYear(), (new Date()).getUTCMonth() + 1, (new Date()).getUTCDate()]);
            xValueAxis.min = 0
            xValueAxis.max = 1
            xDateAxis.min = Date(earliest)
            xDateAxis.max = Date(newest)
        }
        else {
            // Trouve la valeur minimale et maximale, en récupérant toutes les valeurs et en les comparants
            var values = []
            for (var splineIndex=0 ; splineIndex < root.datas.length ; splineIndex++) {
                for (var pointIndex=0 ; pointIndex < root.datas[splineIndex].length ; pointIndex++) {
                    values.append(root.datas[splineIndex][pointIndex][0])
                }
            }
            var smallest = values.reduce(function (previous, current) {
                return previous > current ? current : previous;
            }, 0);
            var biggest = values.reduce(function (previous, current) {
                return previous < current ? current : previous;
            }, 0);
            xValueAxis.min = smallest
            xValueAxis.max = biggest
            xDateAxis.min = Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
            xDateAxis.max = Date()
        }

        // Redéfinit la valeur maximale de l'axe y (la valeur minimale sera toujours de 0
        // Trouve la valeur minimale et maximale, en récupérant toutes les valeurs et en les comparants
        var values = []
        for (var splineIndex=0 ; splineIndex < root.datas.length ; splineIndex++) {
            for (var pointIndex=0 ; pointIndex < root.datas[splineIndex].length ; pointIndex++) {
                values.append(root.datas[splineIndex][pointIndex][1])
            }
        }
        var biggest = values.reduce(function (previous, current) {
            return previous < current ? current : previous;
        }, 0);
        yValueAxis.max = biggest
    }

    // Détecte lorsque la liste des splines est mise à jour, ajoute un delai avant l'appel et met à jour les limites et les valeurs
    onDatasChanged: delayTimer.start()

    Timer {
        id: delayTimer

        interval: 50; repeat: false
        onTriggered: {
            // Redéfinit les valeurs limites des graphiques
            root.updateLimits()

            // Passe sur chacune des bars et la met à jour
            for (var chartIndex=0 ; chartIndex < charts.count ; chartIndex++) {
                root.updateValues(chartIndex)
            }
        }
    }



    // Repeater pour afficher toutes les splines
    Repeater {
        id: charts

        anchors.fill: parent

        // Autant de graphiques qu'il y a de courbes à afficher
        model: Math.min(root.datas.length, root.names.length, root.colors.length)

        // ChartView permettant d'afficher la structure du ghraphe
        ChartView {
            // Propriété permettant de connaitre l'index du graphique
            readonly property int splineIndex: index


            // Fonctions permettant de rajouter et d'enlever des points à la SplineSeries
            // Il est impossible pour la fonction updateValues de récupérer la spline
            function clear() { spline.removePoints(0, spline.count) }
            function addPoint(x, y) { spline.append(x, y) }

            // Légende redéfinie manuellement
            legend.visible: false

            // Fait que le composant prenne la taille indiquée (en laissant 32px de marge en bas et à gauche pour les axes)
            anchors.fill: parent
            anchors.bottomMargin: 50                // Laisse assez d'espace pour la légende
            plotAreaColor: "transparent"
            backgroundColor: "transparent"

            // Enlève les bordures pour éviter à certaines valeurs de disparaitre
            margins.top: 0
            margins.bottom: 0
            margins.left: 0
            margins.right: 0

            // Active l'antialiasing pour un bon rendu même en petites dimensions
            antialiasing: true



            // SplineSeries pour tracer la courbe
            LineSeries {
                id: spline

                // La répétition de point et de SplineSeries est impossible (car ce sont des delegates et non des objets)
                // Ceci devront être rajoutés avec l'appel de la fonction updatevalues()

                // Couleur de la courbe (dépend des couleurs envoyées)
                color: root.colors[splineIndex]

                // Définit les axes, selon l'index
                axisX: ValueAxis {
                    // Les valeurs minimales et maximales sont redéfinies lors de la mise à jour des données
                    min: root.xMinimum
                    max: root.xMaximum

                    color: root.textEnabledColor
                    gridLineColor: root.textDisabledColor
                    gridVisible: true
                    lineVisible: true
                    tickCount: Math.max(root.xTicks, 2)
                    minorTickCount: Math.max(root.xMinorTicks, 0)

                    labelsColor: root.textEnabledColor
                    minorGridLineColor: root.textDisabledColor
                    labelFormat: `%.${root.xDecimals}f`
                    labelsVisible: !root.xAxisDateFormat

                    titleText: `<font color='${root.textEnabledColor}'>${root.xTitle}</font>`
                    titleFont.pixelSize: root.titleFontSize
                    titleVisible: true
                }

                axisY: ValueAxis {
                    // Les valeurs minimales et maximales sont redéfinies lors de la mise à jour des données
                    min: root.yMinimum
                    max: root.yMaximum

                    color: root.textEnabledColor
                    gridLineColor: root.textDisabledColor
                    gridVisible: true
                    lineVisible: true
                    tickCount: Math.max(root.yTicks, 2)
                    minorTickCount: Math.max(root.yMinorTicks, 0)
                    labelsVisible: true

                    labelsColor: root.textEnabledColor
                    minorGridLineColor: root.textDisabledColor
                    labelFormat: `%.${root.yDecimals}f`

                    titleText: `<font color='${root.textEnabledColor}'>${root.yTitle}</font>`
                    titleFont.pixelSize: root.titleFontSize
                    titleVisible: true
                }
            }
        }
    }

    // Fais une première update de toutes les splines pour les montrer une fois le composant chargé
    Component.onCompleted: {root.updateLimits(); root.updateValues(-1) }


    // Repeater pour afficher les dates, si l'utilisateur préfère afficher les axes des X comme dates
    Repeater {
        id: xAxisDate

        model: Math.max(root.xTicks, 2)

        Text {
            x: root.x + 40 +  3 * root.fontSize + (root.width - 40 - 3 * root.fontSize) * index / (Math.max(root.xTicks, 2) - 1) - 30
            y: root.y + root.height - 3 * root.fontSize - 40 - 5

            readonly property var date: new Date(parseInt(root.xMinimum + index / (Math.max(root.xTicks, 2) - 1) * (root.xMaximum - root.xMinimum)))
            text: `${date.getUTCDate()}-${date.getUTCMonth() + 1}-${date.getUTCFullYear()}`

            color: root.textEnabledColor
            font.pixelSize: root.fontSize
            font.family: "Verdana"
            visible: root.xAxisDateFormat
        }
    }

    Repeater {
        id: legend

        model: Math.min(root.names.length, root.colors.length)


        Item {
            Rectangle {
                x: root.x + 300 * (index % 3) + 40
                y: root.y + root.height + root.fontSize * 2 * parseInt(index / 3) - 40 - 15
                width: root.fontSize
                height: root.fontSize

                color: root.colors[index]
                border.width: 1
                border.color: root.textEnabledColor
            }

            Text {
                x: root.x + 300 * (index % 3) + 2 * root.fontSize + 40
                y: root.y + root.height + root.fontSize * 2 * parseInt(index / 3) - 40 - 15
                width: root.fontSize
                height: root.fontSize

                text: root.names[index]
                color: index < root.datas.length ? root.textEnabledColor : root.textDisabledColor
            }
        }
    }
}
