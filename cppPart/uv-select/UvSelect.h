#ifndef UVSELECT_H
#define UVSELECT_H

#include <QVariant>

#include "KisActionPlugin.h"
#include "KisSelectionTags.h"

class UvSelect : public KisActionPlugin
{
    Q_OBJECT

public:
    UvSelect(QObject *parent, const QVariantList &);
    ~UvSelect() override;
    void selectPolygon(QVector<QPointF> &points,SelectionAction actionMode);
    void selectPolygons(QVector<QVector<QPointF>> &pointsList,SelectionAction actionMode);
private Q_SLOTS:
    void slotSample(bool sampleRealCanvas);

public:
    KisAction *action;
};

#endif // UVSELECT_H
