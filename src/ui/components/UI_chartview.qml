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
    property var splinesData: []                // Données des SplineSeries. Format: [[[x11, y11], [x12, y12], ...], ...] ou [[[[year11, month11, day11], y11], [[year12, month12, day12], y12], ...], ...]
    property var splinesLegend:  []             // Légendes des SplineSeries. Format: [["color (hex)", "name"], ...]
    property var barsData: []                   // Données des BarSeries. Format: [[[x11, y11], [x12, y12], ...], ...] ou [[[[year11, month11, day11], y11], [[year12, month12, day12], y12], ...], ...]
    property var barsLegend:  []                // Légendes des barsSeries. Format: [["color (hex)", "name"], ...]
    readonly property bool dateFormat: splinesData.length > 0 && splinesData[0].length > 0 && isNaN(splinesData[0][0][0])

    // Propriétés sur les axes (axes communs pour x et séparés pour y)
    property string xTitle: ""
    property int xDecimals: 2
    property int xTicks: 4
    property int xMinorTicks: 0
    property string ySplinesTitle: ""
    property int ySplinesDecimals: 2
    property int ySplinesTicks: 4
    property int ySplinesMinorTicks: 0
    property string yBarsTitle: ""
    property int yBarsDecimals: 2
    property int yBarsTicks: 4
    property int yBarsMinorTicks: 0
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
    function updateSpline(spline) {      // Index de 0 à Nsplines - 1
        // Définit les limites des splines à mettre à jour (celle indiquée ou toutes si l'index est invalide)
        // splinesChart.model = root.splinesData.length ; cependant les composants des Repeater ne sont chargés qu'après chargement complet du composant
        var from = spline >= 0 && spline < splinesChart.count ? spline : 0
        var to = spline >= 0 && spline < splinesChart.count ? spline : splinesChart.count - 1

        // Pour toutes les splines à mettre à jour (toutes, où celle à l'index existant, s'il est valide)
        for (var chart = from ; chart <= to ; chart++) {
            // Réinitialise la spline
            splinesChart.itemAt(chart).clear()

            // Rajoute tous les nouveaux points
            for (var point = 0 ; point < root.splinesData[chart].length ; point++) {
                splinesChart.itemAt(chart).addPoint(root.splinesData[chart][point][0],
                                                    root.splinesData[chart][point][1])
            }
        }
    }

    // Fonction pour mettre à jour une bar (ou toutes si index invalide)
    // La mise à jour est manuelle car catastrophiquement lente
    function updateBar(bar) {      // Index de 0 à Nbars - 1
        // Définit les limites des bars à mettre à jour (celle indiquée ou toutes si l'index est invalide)
        // barsChart.model = root.barsData.length ; cependant les composants des Repeater ne sont chargés qu'après chargement complet du composant
        var from = bar >= 0 && bar < barsChart.count ? bar : 0
        var to = bar >= 0 && bar < barsChart.count ? bar : barsChart.count - 1

        // Pour toutes les bar à mettre à jour (toutes, où celle à l'index existant, s'il est valide)
        for (var chart = from ; chart <= to ; chart++) {
            // Réinitialise la bar
            barsChart.itemAt(chart).clear()

            // Rajoute tous les nouveaux points
            for (var point = 0 ; point < root.barsData[chart].length ; point++) {
                barsChart.itemAt(chart).addPoint(root.barsData[chart][point][0],
                                                 root.barsData[chart][point][1])
            }
        }
    }


    // Détecte lorsque la liste des splines est mise à jour
    onSplinesDataChanged: {
        // Redéfinit les valeurs minimales et maximales
        //TODO : implémenter

        // Passe sur chacune des bars et la met à jour
        for (var chart=0 ; chart < splinesChart.count ; chart++) {
            root.updateSpline(chart)
        }
    }

    // Détecte lorsque la liste des légendes des splines est mise à jour
    onSplinesLegendChanged: {
        // Passe sur chacune des bars et la met à jour
        for (var chart=0 ; chart < splinesChart.count ; chart++) {
            root.updateSpline(chart)
        }
    }

    // Détecte lorsque la liste des bars est mise à jour
    onBarsDataChanged: {
        // Redéfinit Les valeurs minimales et maximales
        // TODO : implémenter

        // Passe sur chacune des bars et la met à jour
        for (var chart=0 ; chart < barsChart.count ; chart++) {
            root.updateBar(chart)
        }
    }

    // Détecte lorsque la liste des légendes des bars est mise à jour
    onBarsLegendChanged: {
        // Passe sur chacune des bars et la met à jour
        for (var chart=0 ; chart < barsChart.count ; chart++) {
            root.updateBar(chart)
        }
    }


    // Liste des différents axes, utilisés par le graphique
    ValueAxis {
        id: xValueAxis

        // Les valeurs minimales et maximales sont redéfinies lors de la mise à jour des données
        min: 0
        max: 1

        color: root.textEnabledColor
        gridLineColor: root.textDisabledColor
        gridVisible: true
        lineVisible: true
        tickCount: Math.max(root.xTicks, 2)
        minorTickCount: Math.max(root.xMinorTicks, 0)

        labelsColor: root.textEnabledColor
        minorGridLineColor: root.textDisabledColor
        labelFormat: `%.${root.xDecimals}f`

        titleText: `<font color='${root.textEnabledColor}'>${root.xTitle}</font>`
        titleFont.pixelSize: root.titleFontSize
    }

    ValueAxis {
        id: xValueInvisible

        // Les valeurs minimales sont les mêmes que la version visible, afin que les valeurs s'allignent bien
        min: xValueAxis.min
        max: xValueAxis.max

        // Cache le composant pour montrer l'axe une unique fois
        visible: false
    }



    DateTimeAxis {
        id: xDateAxis

        // Les valeurs minimales et maximales sont redéfinies lors de la mise à jour des données
        min: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
        max: new Date()

        color: root.textEnabledColor
        gridLineColor: root.textDisabledColor
        gridVisible: true
        lineVisible: true
        tickCount: Math.max(root.xTicks, 2)

        labelsColor: root.textEnabledColor
        minorGridLineColor: root.textDisabledColor
        format: "dd/MM/yyyy"

        titleText: `<font color='${root.textEnabledColor}'>${root.xTitle}</font>`
        titleFont.pixelSize: root.titleFontSize
    }

    DateTimeAxis {
        id: xDateInvisible

        // Les valeurs minimales sont les mêmes que la version visible, afin que les valeurs s'allignent bien
        min: xDateAxis.min
        max: xDateAxis.max

        // Cache le composant pour montrer l'axe une unique fois
        visible: false
    }

    // axe Y pour les splineSeries
    ValueAxis {
        id: ySplinesValueAxis

        // Les valeurs minimales et maximales sont redéfinies lors de la mise à jour des données
        min: 0
        max: 1

        color: root.textEnabledColor
        gridLineColor: root.textDisabledColor
        gridVisible: true
        lineVisible: true
        tickCount: Math.max(root.ySplinesTicks, 2)
        minorTickCount: Math.max(root.ySplinesMinorTicks, 0)

        labelsColor: root.textEnabledColor
        minorGridLineColor: root.textDisabledColor
        labelFormat: `%.${root.ySplinesDecimals}f`

        titleText: `<font color='${root.textEnabledColor}'>${root.ySplinesTitle}</font>`
        titleFont.pixelSize: root.titleFontSize
    }

    ValueAxis {
        id: ySplinesValueInvisible

        // Les valeurs minimales sont les mêmes que la version visible, afin que les valeurs s'allignent bien
        min: ySplinesValueAxis.min
        max: ySplinesValueAxis.max

        // Cache le composant pour montrer l'axe une unique fois
        visible: false
    }

    // axe Y pour les barSeries
    ValueAxis {
        id: yBarsValueAxis

        // Les valeurs minimales et maximales sont redéfinies lors de la mise à jour des données
        min: 0
        max: 1

        color: root.textEnabledColor
        gridLineColor: root.textDisabledColor
        gridVisible: true
        lineVisible: true
        tickCount: Math.max(root.yBarsTicks, 2)
        minorTickCount: Math.max(root.yBarsMinorTicks, 0)

        labelsColor: root.textEnabledColor
        minorGridLineColor: root.textDisabledColor
        labelFormat: `%.${root.yBarsDecimals}f`

        titleText: `<font color='${root.textEnabledColor}'>${root.yBarsTitle}</font>`
        titleFont.pixelSize: root.titleFontSize
    }

    ValueAxis {
        id: yBarsValueInvisible

        // Les valeurs minimales sont les mêmes que la version visible, afin que les valeurs s'allignent bien
        min: yBarsValueAxis.min
        max: yBarsValueAxis.max

        // Cache le composant pour montrer l'axe une unique fois
        visible: false
    }


    // Repeater pour afficher toutes les splines
    Repeater {
        id: splinesChart

        anchors.fill: parent

        // Autant de graphiques qu'il y a de courbes à afficher
        model: Math.min(root.splinesData.length, root.splinesLegend.length)

        // ChartView permettant d'afficher la structure du ghraphe
        ChartView {
            // Propriété permettant de connaitre l'index du graphique
            readonly property int splineIndex: index


            // Fonctions permettant de rajouter et d'enlever des points à la SplineSeries
            // Il est impossible pour la fonction updateSpline de récupérer la spline
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
                // Ceci devront être rajoutés avec l'appel de la fonction updateSpline()

                // Couleur de la courbe (dépend des couleurs envoyées)
                color: root.splinesLegend[splineIndex][0]

                // Définit les axes, selon l'index
                axisX: splineIndex == 0 ? (root.dateFormat ? xDateAxis : xValueAxis) : (root.dateFormat ? xDateInvisible : xValueInvisible)      // FIXME : faire attention au changement de valeurs
                axisY: splineIndex == 0 ? ySplinesValueAxis : ySplinesValueInvisible
            }
        }
    }

    // Fais une première update de toutes les splines pour les montrer une fois le composant chargé
    Component.onCompleted: { root.updateSpline(-1); root.updateBar(-1); }
}
