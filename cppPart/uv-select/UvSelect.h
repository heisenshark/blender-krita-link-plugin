/*
 *  SPDX-FileCopyrightText: 2023 killy |0veufOrever <80536642@qq.com>
 *  SPDX-FileCopyrightText: 2023 Deif Lou <ginoba@gmail.com>
 *
 *  SPDX-License-Identifier: GPL-2.0-or-later
 */

#ifndef KISSAMP_H
#define KISSAMP_H

#include <QVariant>

#include "KisActionPlugin.h"
// #include "kis_types.h"
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

#endif // KISSAMP_H
