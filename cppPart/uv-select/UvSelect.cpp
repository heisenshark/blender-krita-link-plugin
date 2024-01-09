/*
 *  SPDX-FileCopyrightText: 2023 killy |0veufOrever <80536642@qq.com>
 *  SPDX-FileCopyrightText: 2023 Deif Lou <ginoba@gmail.com>
 *
 *  SPDX-License-Identifier: GPL-2.0-or-later
 */

#include "UvSelect.h"

#include <kpluginfactory.h>
#include <kis_action.h>
#include <kis_canvas_resource_provider.h>
#include <KisViewManager.h>
#include <KoPathShape.h>

#include "kis_algebra_2d.h"
#include "kis_painter.h"
#include <brushengine/kis_paintop_registry.h>
#include "kis_selection_options.h"
#include "kis_canvas2.h"
#include "kis_pixel_selection.h"
#include "kis_selection_tool_helper.h"
#include "kis_shape_tool_helper.h"
#include "kis_tool.h"
#include "kis_default_bounds.h"
#include "kis_selection.h"

#include "KisViewManager.h"
#include "kis_selection_manager.h"
#include "KisSelectionTags.h"
#include "kis_command_utils.h"
#include "kis_selection_filters.h"
#include <QList>

#include <iostream>

K_PLUGIN_FACTORY_WITH_JSON(UVselectFactory, "kritashapesselection.json", registerPlugin<UvSelect>();)

UvSelect::UvSelect(QObject *parent, const QVariantList &)
    : KisActionPlugin(parent)
{
    std::cout<<"AAAAAAAAAAAA\n";
    action = createAction("select_shapes");
    connect(action, &QAction::triggered, [this](){ slotSample(false); });
}

UvSelect::~UvSelect()
{}

void UvSelect::slotSample(bool sampleRealCanvas)
{
    QVector<QPointF> p;
    p << QPointF(0.0, 0.0) <<QPointF(0.0, 0.0) <<QPointF(0.0, 0.0)<<QPointF(0.0, 0.0);
    selectPolygon(p,SELECTION_REPLACE);
    QVariant v = action->data();
    std::cout<< "Type: " <<v.type()<<"\n";
    std::cout<< "Akcja: \n";
    if(v.type()==QMetaType::QVariantList)
    {
        auto polygons = v.toList();
        QVector<QVector<QPointF>> pointsList;
        for(QVariant polygon: polygons){
            QVector<QPointF> cds;
            auto points = polygon.toList();
            for(QVariant point: points){
                auto coords = point.toList();
                std::cout<< coords[0].toDouble()<< " , " <<coords[1].toDouble()<<";";
                cds<<QPointF(coords[0].toDouble(),coords[1].toDouble());
            }
            std::cout<<"\n----\n";
            pointsList << cds;
        }
        selectPolygons(pointsList,SELECTION_ADD);
    }

}

void UvSelect::selectPolygon(QVector<QPointF> &points,SelectionAction actionMode)
{
    KisCanvas2 * kisCanvas = viewManager()->canvasBase();
    auto image = viewManager()->image();
    auto node = viewManager()->activeNode();
    Q_ASSERT(kisCanvas);
    if (!kisCanvas)
        return;

    // const QRectF boundingViewRect = pixelToView(KisAlgebra2D::accumulateBounds(points));

    KisSelectionToolHelper helper(kisCanvas, kundo2_i18n("Select Polygon"));

    // if (helper.tryDeselectCurrentSelection(pixelToView(boundingViewRect), 0)) {
    //     return;
    // }

    KoPathShape* path = new KoPathShape();
    path->setShapeId(KoPathShapeId);

    QTransform resolutionMatrix;
    resolutionMatrix.scale(1 / image->xRes(), 1 / image->yRes());
    path->moveTo(resolutionMatrix.map(points[0]));
    for (int i = 1; i < points.count(); i++)
        path->lineTo(resolutionMatrix.map(points[i]));
    path->close();
    path->normalize();

    helper.addSelectionShape(path, actionMode);
}

void UvSelect::selectPolygons(QVector<QVector<QPointF>> &pointsList,SelectionAction actionMode)
{
    KisCanvas2 * kisCanvas = viewManager()->canvasBase();
    auto image = viewManager()->image();
    auto node = viewManager()->activeNode();
    Q_ASSERT(kisCanvas);
    if (!kisCanvas)
        return;

    // const QRectF boundingViewRect = pixelToView(KisAlgebra2D::accumulateBounds(points));

    KisSelectionToolHelper helper(kisCanvas, kundo2_i18n("Select Polygon"));

    // if (helper.tryDeselectCurrentSelection(pixelToView(boundingViewRect), 0)) {
    //     return;
    // }

    QList<KoShape*> shapes;
    for(QVector<QPointF> points: pointsList){
        KoPathShape* path = new KoPathShape();
        path->setShapeId(KoPathShapeId);

        QTransform resolutionMatrix;
        resolutionMatrix.scale(1 / image->xRes(), 1 / image->yRes());
        path->moveTo(resolutionMatrix.map(points[0]));
        for (int i = 1; i < points.count(); i++)
            path->lineTo(resolutionMatrix.map(points[i]));
        path->close();
        path->normalize();
        shapes<<path;
    }
    helper.addSelectionShapes(shapes, actionMode);
    // qDeleteAll(shapes);
    // QList<KoShape*>::iterator i;
    // for (i = shapes.begin(); i != shapes.end(); i++) {
    //     delete (*i);
    // }

    // for(KoShape* s: shapes) {
    //     std::cout << s<<"\n";
    //     // delete s;
    // }
}

#include "UvSelect.moc"


    // KisScreenColorSampler *screenColorSampler = new KisScreenColorSampler(false);
    // screenColorSampler->setPerformRealColorSamplingOfCanvas(sampleRealCanvas);
    // screenColorSampler->setCurrentColor(viewManager()->canvasResourceProvider()->fgColor());
    // // screenColorSampler is a temporary top level widget own by no other
    // // QObject, so it must be automatically deleted when it is closed 
    // screenColorSampler->setAttribute(Qt::WA_DeleteOnClose);
    // connect(screenColorSampler, &KisScreenColorSampler::sigNewColorSampled,
    //     [this, screenColorSampler](KoColor sampledColor)
    //     {
    //         viewManager()->canvasResourceProvider()->slotSetFGColor(sampledColor);
    //         screenColorSampler->close();
    //     }
    // );
    // connect(screenColorSampler, &KisScreenColorSampler::sigNewColorHovered,
    //     [this, screenColorSampler](KoColor sampledColor)
    //     {
    //         viewManager()->canvasResourceProvider()->slotSetFGColor(sampledColor);
    //     }
    // );
    // screenColorSampler->sampleScreenColor();
