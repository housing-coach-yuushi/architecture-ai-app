/**
 * キャンバスレンダラー - 2D描画を担当
 */
export class CanvasRenderer {
    constructor(ctx, width, height) {
        this.ctx = ctx;
        this.width = width;
        this.height = height;

        // ビュー変換
        this.scale = 50; // 1m = 50px
        this.offsetX = width / 2;
        this.offsetY = height / 2;
    }

    /**
     * 画面座標 → ワールド座標
     */
    screenToWorld(sx, sy) {
        return {
            x: (sx - this.offsetX) / this.scale,
            y: -(sy - this.offsetY) / this.scale, // Y軸反転
        };
    }

    /**
     * ワールド座標 → 画面座標
     */
    worldToScreen(wx, wy) {
        return {
            x: wx * this.scale + this.offsetX,
            y: -wy * this.scale + this.offsetY, // Y軸反転
        };
    }

    /**
     * ズームイン
     */
    zoomIn(centerX, centerY) {
        const oldScale = this.scale;
        this.scale *= 1.5;
        if (this.scale > 800) this.scale = 800;

        if (centerX !== undefined && centerY !== undefined) {
            // 指定座標を中心にズーム
            this.offsetX -= (centerX - this.offsetX) * (this.scale / oldScale - 1);
            this.offsetY -= (centerY - this.offsetY) * (this.scale / oldScale - 1);
        }
    }

    /**
     * ズームアウト
     */
    zoomOut(centerX, centerY) {
        const oldScale = this.scale;
        this.scale /= 1.5;
        if (this.scale < 2) this.scale = 2;

        if (centerX !== undefined && centerY !== undefined) {
            // 指定座標を中心にズーム
            this.offsetX -= (centerX - this.offsetX) * (this.scale / oldScale - 1);
            this.offsetY -= (centerY - this.offsetY) * (this.scale / oldScale - 1);
        }
    }

    /**
     * パン（平行移動）
     */
    pan(dx, dy) {
        this.offsetX += dx;
        this.offsetY += dy;
    }

    /**
     * ポリゴンにフィット
     */
    fitToPolygon(polygon) {
        if (polygon.length === 0) return;

        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;

        polygon.forEach(p => {
            minX = Math.min(minX, p[0]);
            maxX = Math.max(maxX, p[0]);
            minY = Math.min(minY, p[1]);
            maxY = Math.max(maxY, p[1]);
        });

        const polygonWidth = maxX - minX;
        const polygonHeight = maxY - minY;
        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;

        // 余白を考慮してスケール計算
        const margin = 0.8;
        const scaleX = (this.width * margin) / polygonWidth;
        const scaleY = (this.height * margin) / polygonHeight;
        this.scale = Math.min(scaleX, scaleY);

        // 中心を画面中央に
        this.offsetX = this.width / 2 - centerX * this.scale;
        this.offsetY = this.height / 2 + centerY * this.scale;
    }

    /**
     * クリア
     */
    clear() {
        this.ctx.fillStyle = '#f8fafc';
        this.ctx.fillRect(0, 0, this.width, this.height);
    }

    /**
     * グリッド描画
     */
    drawGrid(gridConfig) {
        if (!gridConfig.visible) return;

        const moduleM = gridConfig.module / 1000; // mm → m

        // ビューポートの範囲をワールド座標で計算
        const topLeft = this.screenToWorld(0, 0);
        const bottomRight = this.screenToWorld(this.width, this.height);

        // グリッドの開始・終了範囲を計算（モジュール単位）
        const startX = Math.floor(topLeft.x / moduleM) * moduleM;
        const endX = Math.ceil(bottomRight.x / moduleM) * moduleM;
        const startY = Math.floor(bottomRight.y / moduleM) * moduleM;
        const endY = Math.ceil(topLeft.y / moduleM) * moduleM;

        this.ctx.strokeStyle = '#e2e8f0';
        this.ctx.lineWidth = 1;

        // 縦線 (浮動小数点の累積誤差を避けるため整数のインデックスで回すのが理想だが、ここでは余裕を持たせた終了条件にする)
        const eps = moduleM * 0.001;
        for (let gx = startX; gx <= endX + eps; gx += moduleM) {
            const screen = this.worldToScreen(gx, 0);
            this.ctx.beginPath();
            this.ctx.moveTo(screen.x, 0);
            this.ctx.lineTo(screen.x, this.height);
            this.ctx.stroke();
        }

        // 横線
        for (let gy = startY; gy <= endY + eps; gy += moduleM) {
            const screen = this.worldToScreen(0, gy);
            this.ctx.beginPath();
            this.ctx.moveTo(0, screen.y);
            this.ctx.lineTo(this.width, screen.y);
            this.ctx.stroke();
        }

        // 原点マーカー
        const origin = this.worldToScreen(0, 0);
        this.ctx.strokeStyle = '#94a3b8';
        this.ctx.lineWidth = 2;

        // X軸
        this.ctx.beginPath();
        this.ctx.moveTo(origin.x - 20, origin.y);
        this.ctx.lineTo(origin.x + 20, origin.y);
        this.ctx.stroke();

        // Y軸
        this.ctx.beginPath();
        this.ctx.moveTo(origin.x, origin.y - 20);
        this.ctx.lineTo(origin.x, origin.y + 20);
        this.ctx.stroke();
    }

    /**
     * 敷地描画
     */
    drawSite(site, tempPoints = []) {
        const polygon = site.polygon;
        const allPoints = [...polygon.map(p => ({ x: p[0], y: p[1] }))];

        // 仮の点も追加
        tempPoints.forEach(p => {
            allPoints.push(p);
        });

        if (allPoints.length === 0) return;

        // 敷地ポリゴン
        if (polygon.length >= 3) {
            this.ctx.beginPath();
            const first = this.worldToScreen(polygon[0][0], polygon[0][1]);
            this.ctx.moveTo(first.x, first.y);

            for (let i = 1; i < polygon.length; i++) {
                const p = this.worldToScreen(polygon[i][0], polygon[i][1]);
                this.ctx.lineTo(p.x, p.y);
            }

            this.ctx.closePath();
            this.ctx.fillStyle = 'rgba(34, 197, 94, 0.1)';
            this.ctx.fill();
            this.ctx.strokeStyle = '#22c55e';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
        }

        // 頂点
        allPoints.forEach((point, index) => {
            const screen = this.worldToScreen(point.x, point.y);

            this.ctx.beginPath();
            this.ctx.arc(screen.x, screen.y, 6, 0, Math.PI * 2);
            this.ctx.fillStyle = index < polygon.length ? '#22c55e' : '#94a3b8';
            this.ctx.fill();
            this.ctx.strokeStyle = 'white';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
        });

        // 仮線
        if (tempPoints.length > 0 && polygon.length > 0) {
            const lastPolygon = this.worldToScreen(
                polygon[polygon.length - 1][0],
                polygon[polygon.length - 1][1]
            );
            const tempScreen = this.worldToScreen(tempPoints[0].x, tempPoints[0].y);

            this.ctx.beginPath();
            this.ctx.moveTo(lastPolygon.x, lastPolygon.y);
            this.ctx.lineTo(tempScreen.x, tempScreen.y);
            this.ctx.strokeStyle = '#94a3b8';
            this.ctx.lineWidth = 1;
            this.ctx.setLineDash([5, 5]);
            this.ctx.stroke();
            this.ctx.setLineDash([]);
        }
    }

    /**
     * 部屋描画（多角形対応）
     */
    drawRooms(rooms, roomTypes, selectedItem) {
        rooms.forEach(room => {
            if (!room.bounds && !room.polygon) return;

            const roomType = roomTypes[room.type];
            const color = roomType?.color || '#888';
            const isSelected = selectedItem && selectedItem.id === room.id;

            // 多角形がある場合は多角形を描画、なければ矩形
            if (room.polygon && room.polygon.length >= 3) {
                this.drawPolygonRoom(room, color, isSelected, roomType);
            } else if (room.bounds) {
                this.drawRectRoom(room, color, isSelected, roomType);
            }
        });
    }

    /**
     * 多角形部屋を描画
     */
    drawPolygonRoom(room, color, isSelected, roomType) {
        const polygon = room.polygon;

        // パスを作成
        this.ctx.beginPath();
        const first = this.worldToScreen(polygon[0][0], polygon[0][1]);
        this.ctx.moveTo(first.x, first.y);

        for (let i = 1; i < polygon.length; i++) {
            const p = this.worldToScreen(polygon[i][0], polygon[i][1]);
            this.ctx.lineTo(p.x, p.y);
        }
        this.ctx.closePath();

        // 塗りつぶし
        if (room._overlapping) {
            this.ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
        } else {
            this.ctx.fillStyle = color + '40';
        }
        this.ctx.fill();

        // 枠線
        if (room._overlapping) {
            this.ctx.strokeStyle = '#ef4444';
            this.ctx.lineWidth = 3;
        } else {
            this.ctx.strokeStyle = isSelected ? '#1d4ed8' : color;
            this.ctx.lineWidth = isSelected ? 3 : 2;
        }
        this.ctx.stroke();

        // リサイズハンドル（選択時のみ）- bounds基準で描画
        if (isSelected && room.bounds) {
            const b = room.bounds;
            const topLeft = this.worldToScreen(b.x, b.y + b.height);
            const bottomRight = this.worldToScreen(b.x + b.width, b.y);
            this.drawResizeHandles(topLeft, bottomRight);
        }

        // ラベル（中心位置）
        const bounds = room.bounds;
        const centerX = (bounds.x + bounds.width / 2);
        const centerY = (bounds.y + bounds.height / 2);
        const center = this.worldToScreen(centerX, centerY);

        this.ctx.fillStyle = '#1e293b';
        this.ctx.font = 'bold 12px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(roomType?.label || room.type, center.x, center.y - 10);

        // 面積表示
        const area = room.target_area || 0;
        this.ctx.font = '11px sans-serif';
        this.ctx.fillStyle = room._overlapping ? '#ef4444' : '#64748b';
        this.ctx.fillText(`${area}㎡`, center.x, center.y + 8);

        // 形状タイプ表示
        if (room.preset_shape && room.preset_shape !== 'rectangle') {
            this.ctx.font = '9px sans-serif';
            this.ctx.fillStyle = '#94a3b8';
            const shapeLabels = { 'L': 'L字型', 'U': 'コの字型' };
            this.ctx.fillText(shapeLabels[room.preset_shape] || '', center.x, center.y + 22);
        }
    }

    /**
     * 矩形部屋を描画
     */
    drawRectRoom(room, color, isSelected, roomType) {
        const topLeft = this.worldToScreen(room.bounds.x, room.bounds.y + room.bounds.height);
        const bottomRight = this.worldToScreen(
            room.bounds.x + room.bounds.width,
            room.bounds.y
        );

        const width = bottomRight.x - topLeft.x;
        const height = bottomRight.y - topLeft.y;

        // 塗りつぶし
        if (room._overlapping) {
            this.ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
        } else {
            this.ctx.fillStyle = color + '40';
        }
        this.ctx.fillRect(topLeft.x, topLeft.y, width, height);

        // 枠線
        if (room._overlapping) {
            this.ctx.strokeStyle = '#ef4444';
            this.ctx.lineWidth = 3;
        } else {
            this.ctx.strokeStyle = isSelected ? '#1d4ed8' : color;
            this.ctx.lineWidth = isSelected ? 3 : 2;
        }
        this.ctx.strokeRect(topLeft.x, topLeft.y, width, height);

        // リサイズハンドル（選択時のみ）
        if (isSelected) {
            this.drawResizeHandles(topLeft, bottomRight);
        }

        // ラベル
        const centerX = topLeft.x + width / 2;
        const centerY = topLeft.y + height / 2;

        this.ctx.fillStyle = '#1e293b';
        this.ctx.font = 'bold 12px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(roomType?.label || room.type, centerX, centerY - 10);

        // 面積表示（リアルタイム更新）
        const area = Math.round(room.bounds.width * room.bounds.height * 10) / 10;
        this.ctx.font = '11px sans-serif';
        this.ctx.fillStyle = room._overlapping ? '#ef4444' : '#64748b';
        this.ctx.fillText(`${area}㎡`, centerX, centerY + 8);

        // サイズ表示
        this.ctx.font = '9px sans-serif';
        this.ctx.fillStyle = '#94a3b8';
        const w = room.bounds.width.toFixed(1);
        const h = room.bounds.height.toFixed(1);
        this.ctx.fillText(`${w}m × ${h}m`, centerX, centerY + 22);
    }

    /**
     * リサイズハンドル描画（4角 + 4辺）
     */
    drawResizeHandles(topLeft, bottomRight) {
        const handleSize = 8;
        const centerX = (topLeft.x + bottomRight.x) / 2;
        const centerY = (topLeft.y + bottomRight.y) / 2;

        // 4角のハンドル（正方形）
        const corners = [
            { x: topLeft.x, y: topLeft.y },           // NW
            { x: bottomRight.x, y: topLeft.y },       // NE
            { x: topLeft.x, y: bottomRight.y },       // SW
            { x: bottomRight.x, y: bottomRight.y },   // SE
        ];

        corners.forEach(handle => {
            this.ctx.fillStyle = '#1d4ed8';
            this.ctx.fillRect(
                handle.x - handleSize / 2,
                handle.y - handleSize / 2,
                handleSize,
                handleSize
            );
            this.ctx.strokeStyle = 'white';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(
                handle.x - handleSize / 2,
                handle.y - handleSize / 2,
                handleSize,
                handleSize
            );
        });

        // 4辺のハンドル（細長い）
        const edgeHandles = [
            { x: centerX, y: topLeft.y, w: 16, h: 6 },     // N
            { x: centerX, y: bottomRight.y, w: 16, h: 6 }, // S
            { x: bottomRight.x, y: centerY, w: 6, h: 16 }, // E
            { x: topLeft.x, y: centerY, w: 6, h: 16 },     // W
        ];

        edgeHandles.forEach(handle => {
            this.ctx.fillStyle = '#60a5fa';  // 薄い青
            this.ctx.fillRect(
                handle.x - handle.w / 2,
                handle.y - handle.h / 2,
                handle.w,
                handle.h
            );
            this.ctx.strokeStyle = 'white';
            this.ctx.lineWidth = 1;
            this.ctx.strokeRect(
                handle.x - handle.w / 2,
                handle.y - handle.h / 2,
                handle.w,
                handle.h
            );
        });
    }

    /**
     * 設備描画（実際の寸法で形状を描画）
     */
    drawUnits(units, selectedItem) {
        // 設備の寸法定義（m単位、FreeCADと同じ）
        const unitSizes = {
            bath: { '1216': [1.2, 1.6], '1616': [1.6, 1.6], '1620': [1.6, 2.0], '1624': [1.6, 2.4], default: [1.6, 1.6] },
            toilet: { standard: [0.8, 1.2], wide: [0.9, 1.4], default: [0.8, 1.2] },
            washstand: { '600': [0.6, 0.5], '750': [0.75, 0.5], '900': [0.9, 0.5], '1200': [1.2, 0.5], default: [0.75, 0.5] },
            kitchen: { 'I_2400': [2.4, 0.65], 'I_2500': [2.5, 0.65], 'I_2700': [2.7, 0.65], 'L_2400': [2.4, 1.8], 'L_2500': [2.5, 1.8], 'island': [2.4, 1.0], default: [2.5, 0.65] },
            stair: { straight: [0.91, 2.73], U_left: [1.82, 2.73], U_right: [1.82, 2.73], default: [0.91, 2.73] },
            dining_table: { '4人': [1.4, 0.8], '6人': [1.8, 0.9], '8人': [2.4, 1.0], default: [1.4, 0.8] },
            sofa: { '2P': [1.6, 0.9], '3P': [2.2, 0.9], 'L字': [2.4, 2.0], default: [2.2, 0.9] },
            tv: { '55型': [1.3, 0.1], '65型': [1.5, 0.1], '75型': [1.7, 0.1], default: [1.3, 0.1] },
        };

        units.forEach(unit => {
            const [wx, wy] = unit.position_hint;
            const pos = this.worldToScreen(wx, wy);
            const isSelected = selectedItem?.type === 'unit' && selectedItem?.id === unit.id;
            const rotation = unit.rotation || 0;

            // サイズ取得
            const sizeMap = unitSizes[unit.unit_type] || { default: [1, 1] };
            const [w, h] = sizeMap[unit.size_preset] || sizeMap.default;
            const wPx = w * this.scale;
            const hPx = h * this.scale;

            this.ctx.save();
            this.ctx.translate(pos.x, pos.y);
            this.ctx.rotate((rotation * Math.PI) / 180);

            // 色設定
            const colors = {
                bath: { fill: '#E0F7FA', stroke: '#00ACC1' },
                toilet: { fill: '#E8F5E9', stroke: '#43A047' },
                washstand: { fill: '#E3F2FD', stroke: '#1976D2' },
                kitchen: { fill: '#FFF3E0', stroke: '#FB8C00' },
                stair: { fill: '#F3E5F5', stroke: '#8E24AA' },
                dining_table: { fill: '#EFEBE9', stroke: '#6D4C41' },
                sofa: { fill: '#FCE4EC', stroke: '#D81B60' },
                tv: { fill: '#263238', stroke: '#37474F' },
            };
            const col = colors[unit.unit_type] || { fill: '#F5F5F5', stroke: '#9E9E9E' };

            // 基本の四角形
            this.ctx.fillStyle = col.fill;
            this.ctx.strokeStyle = isSelected ? '#1d4ed8' : col.stroke;
            this.ctx.lineWidth = isSelected ? 3 : 2;
            this.ctx.fillRect(-wPx / 2, -hPx / 2, wPx, hPx);
            this.ctx.strokeRect(-wPx / 2, -hPx / 2, wPx, hPx);

            // タイプ別の詳細描画
            this.ctx.strokeStyle = col.stroke;
            this.ctx.lineWidth = 1;

            if (unit.unit_type === 'bath') {
                // 浴槽の内側ライン
                const margin = 0.15 * this.scale;
                this.ctx.strokeRect(-wPx / 2 + margin, -hPx / 2 + margin, wPx - margin * 2, hPx - margin * 2);
                // シャワー位置を示す円
                this.ctx.beginPath();
                this.ctx.arc(wPx / 4, -hPx / 4, 0.1 * this.scale, 0, Math.PI * 2);
                this.ctx.stroke();
            } else if (unit.unit_type === 'toilet') {
                // 便器形状
                const bowlW = wPx * 0.6;
                const bowlH = hPx * 0.6;
                this.ctx.beginPath();
                this.ctx.ellipse(0, hPx / 6, bowlW / 2, bowlH / 2, 0, 0, Math.PI * 2);
                this.ctx.stroke();
                // タンク
                this.ctx.fillStyle = col.stroke + '40';
                this.ctx.fillRect(-wPx / 3, -hPx / 2, wPx * 2 / 3, hPx / 4);
            } else if (unit.unit_type === 'washstand') {
                // シンク
                const sinkW = wPx * 0.5;
                const sinkH = hPx * 0.6;
                this.ctx.beginPath();
                this.ctx.ellipse(0, 0, sinkW / 2, sinkH / 2, 0, 0, Math.PI * 2);
                this.ctx.stroke();
                // 蛇口
                this.ctx.beginPath();
                this.ctx.arc(0, -hPx / 3, 0.05 * this.scale, 0, Math.PI * 2);
                this.ctx.fill();
            } else if (unit.unit_type === 'kitchen') {
                // シンク
                this.ctx.strokeRect(-wPx / 4, -hPx / 3, wPx / 4, hPx * 2 / 3);
                // コンロ（3口）
                const burnerR = 0.08 * this.scale;
                for (let i = 0; i < 3; i++) {
                    this.ctx.beginPath();
                    this.ctx.arc(wPx / 6 + i * burnerR * 2.5, 0, burnerR, 0, Math.PI * 2);
                    this.ctx.stroke();
                }
                // L型の場合
                if (unit.size_preset?.startsWith('L_')) {
                    this.ctx.strokeRect(-wPx / 2, hPx / 2 - 0.3 * this.scale, 0.65 * this.scale, hPx - 0.65 * this.scale);
                }
            } else if (unit.unit_type === 'stair') {
                const preset = unit.size_preset || 'straight';
                const arrowSize = 0.12 * this.scale;

                // 共通：CAD標準の登り矢印を描画する関数
                const drawArrow = (startX, startY, endX, endY) => {
                    // 始点に円
                    this.ctx.beginPath();
                    this.ctx.arc(startX, startY, arrowSize * 0.6, 0, Math.PI * 2);
                    this.ctx.stroke();
                    // 矢印の線
                    this.ctx.beginPath();
                    this.ctx.moveTo(startX, startY);
                    this.ctx.lineTo(endX, endY);
                    this.ctx.stroke();
                    // 矢印の先端
                    const angle = Math.atan2(endY - startY, endX - startX);
                    this.ctx.beginPath();
                    this.ctx.moveTo(endX, endY);
                    this.ctx.lineTo(endX - arrowSize * Math.cos(angle - 0.4), endY - arrowSize * Math.sin(angle - 0.4));
                    this.ctx.moveTo(endX, endY);
                    this.ctx.lineTo(endX - arrowSize * Math.cos(angle + 0.4), endY - arrowSize * Math.sin(angle + 0.4));
                    this.ctx.stroke();
                };

                // 共通：破断線（ジグザグ）を描画する関数
                const drawBreakLine = (x1, y1, x2, y2) => {
                    const segments = 4;
                    const dx = (x2 - x1) / segments;
                    const dy = (y2 - y1) / segments;
                    const perpX = -dy * 0.3;
                    const perpY = dx * 0.3;

                    this.ctx.beginPath();
                    this.ctx.moveTo(x1, y1);
                    for (let i = 1; i < segments; i++) {
                        const sign = i % 2 === 1 ? 1 : -1;
                        this.ctx.lineTo(x1 + dx * i + perpX * sign, y1 + dy * i + perpY * sign);
                    }
                    this.ctx.lineTo(x2, y2);
                    this.ctx.stroke();
                };

                if (preset === 'straight') {
                    // 直線階段
                    const stepCount = 13;
                    const stepH = hPx / stepCount;
                    // 段を描画
                    for (let i = 0; i <= stepCount; i++) {
                        this.ctx.beginPath();
                        this.ctx.moveTo(-wPx / 2, -hPx / 2 + i * stepH);
                        this.ctx.lineTo(wPx / 2, -hPx / 2 + i * stepH);
                        this.ctx.stroke();
                    }
                    // 破断線（中央付近）
                    this.ctx.lineWidth = 2;
                    drawBreakLine(-wPx / 2, 0, wPx / 2, 0);
                    this.ctx.lineWidth = 1;
                    // 上り矢印（下から上へ）
                    drawArrow(0, hPx / 2 - arrowSize, 0, -hPx / 2 + arrowSize);

                } else if (preset === 'U_left' || preset === 'U_right') {
                    // U字階段（左回り/右回り）
                    const isLeft = preset === 'U_left';
                    const thirdH = hPx / 3;
                    const leftX = -wPx / 2;
                    const rightX = wPx / 2;
                    const midX = 0;

                    // 左回り: 左側で上り → 踊り場 → 右側で下り（全体で見ると左に回る）
                    // 右回り: 右側で上り → 踊り場 → 左側で下り（全体で見ると右に回る）
                    const startSide = isLeft ? leftX : rightX;
                    const endSide = isLeft ? rightX : leftX;
                    const arrowStartX = isLeft ? -wPx / 4 : wPx / 4;
                    const arrowEndX = isLeft ? wPx / 4 : -wPx / 4;

                    // 一段目（上り側）
                    for (let i = 0; i <= 5; i++) {
                        this.ctx.beginPath();
                        this.ctx.moveTo(startSide, hPx / 2 - i * thirdH / 5);
                        this.ctx.lineTo(midX, hPx / 2 - i * thirdH / 5);
                        this.ctx.stroke();
                    }
                    // 踊り場（上部）
                    this.ctx.fillStyle = col.fill;
                    this.ctx.fillRect(-wPx / 2, -hPx / 2, wPx, thirdH);
                    this.ctx.strokeRect(-wPx / 2, -hPx / 2, wPx, thirdH);
                    // 二段目（下り側）
                    for (let i = 0; i <= 5; i++) {
                        this.ctx.beginPath();
                        this.ctx.moveTo(midX, -hPx / 6 + i * thirdH / 5);
                        this.ctx.lineTo(endSide, -hPx / 6 + i * thirdH / 5);
                        this.ctx.stroke();
                    }
                    // U字矢印
                    this.ctx.lineWidth = 2;
                    this.ctx.beginPath();
                    this.ctx.arc(arrowStartX, hPx / 2 - arrowSize, arrowSize * 0.6, 0, Math.PI * 2);
                    this.ctx.stroke();
                    this.ctx.beginPath();
                    this.ctx.moveTo(arrowStartX, hPx / 2 - arrowSize);
                    this.ctx.lineTo(arrowStartX, -hPx / 3);
                    this.ctx.lineTo(arrowEndX, -hPx / 3);
                    this.ctx.lineTo(arrowEndX, hPx / 2 - arrowSize * 2);
                    this.ctx.stroke();
                    // 矢印の先端
                    this.ctx.beginPath();
                    this.ctx.moveTo(arrowEndX, hPx / 2 - arrowSize * 2);
                    this.ctx.lineTo(arrowEndX - arrowSize * 0.5, hPx / 2 - arrowSize * 3);
                    this.ctx.moveTo(arrowEndX, hPx / 2 - arrowSize * 2);
                    this.ctx.lineTo(arrowEndX + arrowSize * 0.5, hPx / 2 - arrowSize * 3);
                    this.ctx.stroke();
                    this.ctx.lineWidth = 1;
                }
            } else if (unit.unit_type === 'dining_table') {
                // 椅子を描画
                const chairSize = 0.15 * this.scale;
                const chairs = unit.size_preset === '4人' ? 4 : (unit.size_preset === '6人' ? 6 : 8);
                this.ctx.fillStyle = col.stroke + '80';
                // 両サイドに椅子
                for (let i = 0; i < chairs / 2; i++) {
                    const xOffset = -wPx / 2 + wPx / (chairs / 2 + 1) * (i + 1);
                    // 上側
                    this.ctx.fillRect(xOffset - chairSize / 2, -hPx / 2 - chairSize - 0.05 * this.scale, chairSize, chairSize);
                    // 下側
                    this.ctx.fillRect(xOffset - chairSize / 2, hPx / 2 + 0.05 * this.scale, chairSize, chairSize);
                }
            } else if (unit.unit_type === 'sofa') {
                const preset = unit.size_preset || '3P';
                this.ctx.fillStyle = col.stroke + '60';

                if (preset === 'L字') {
                    // L字ソファ：メイン部分
                    const mainW = wPx * 0.6;
                    const mainH = hPx * 0.45;
                    const legW = wPx * 0.4;
                    const legH = hPx * 0.45;

                    // 座面（L字形状）
                    this.ctx.fillStyle = col.fill;
                    this.ctx.beginPath();
                    this.ctx.moveTo(-wPx / 2, -hPx / 2);
                    this.ctx.lineTo(wPx / 2, -hPx / 2);
                    this.ctx.lineTo(wPx / 2, -hPx / 2 + mainH);
                    this.ctx.lineTo(-wPx / 2 + mainW, -hPx / 2 + mainH);
                    this.ctx.lineTo(-wPx / 2 + mainW, hPx / 2);
                    this.ctx.lineTo(-wPx / 2, hPx / 2);
                    this.ctx.closePath();
                    this.ctx.fill();
                    this.ctx.strokeStyle = col.stroke;
                    this.ctx.stroke();

                    // 背もたれ（上辺）
                    this.ctx.fillStyle = col.stroke + '60';
                    this.ctx.fillRect(-wPx / 2, -hPx / 2, wPx, hPx * 0.15);
                    // 背もたれ（左辺）
                    this.ctx.fillRect(-wPx / 2, -hPx / 2, wPx * 0.1, hPx);
                } else {
                    // 通常ソファ（2P, 3P）
                    // 背もたれ
                    this.ctx.fillRect(-wPx / 2, -hPx / 2, wPx, hPx * 0.25);
                    // 左アーム
                    this.ctx.fillRect(-wPx / 2, -hPx / 2, wPx * 0.1, hPx);
                    // 右アーム
                    this.ctx.fillRect(wPx / 2 - wPx * 0.1, -hPx / 2, wPx * 0.1, hPx);
                    // クッション区切り
                    const cushions = preset === '2P' ? 2 : 3;
                    for (let i = 1; i < cushions; i++) {
                        this.ctx.beginPath();
                        this.ctx.moveTo(-wPx / 2 + wPx * 0.1 + (wPx * 0.8 / cushions) * i, -hPx / 2 + hPx * 0.25);
                        this.ctx.lineTo(-wPx / 2 + wPx * 0.1 + (wPx * 0.8 / cushions) * i, hPx / 2);
                        this.ctx.strokeStyle = col.stroke + '60';
                        this.ctx.stroke();
                    }
                }
            } else if (unit.unit_type === 'tv') {
                // TVスタンド or 壁掛け
                this.ctx.fillStyle = '#455A64';
                this.ctx.fillRect(-wPx / 6, hPx / 2, wPx / 3, 0.15 * this.scale);
            }

            // 選択時のハイライト
            if (isSelected) {
                this.ctx.strokeStyle = '#1d4ed8';
                this.ctx.lineWidth = 2;
                this.ctx.setLineDash([4, 4]);
                this.ctx.strokeRect(-wPx / 2 - 4, -hPx / 2 - 4, wPx + 8, hPx + 8);
                this.ctx.setLineDash([]);
            }

            this.ctx.restore();

            // ラベル（日本語に変換）
            const labelMap = {
                straight: '直線', U_left: 'U字(左)', U_right: 'U字(右)',
                standard: '標準', wide: 'ワイド', island: 'アイランド',
            };
            const labelText = labelMap[unit.size_preset] || unit.size_preset;
            this.ctx.font = '10px sans-serif';
            this.ctx.fillStyle = '#1e293b';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(labelText, pos.x, pos.y + hPx / 2 + 15);

            // 回転角度表示（選択時）
            if (isSelected && rotation !== 0) {
                this.ctx.fillStyle = '#1d4ed8';
                this.ctx.font = 'bold 9px sans-serif';
                this.ctx.fillText(`${rotation}°`, pos.x, pos.y + hPx / 2 + 27);
            }
        });
    }

    /**
     * サイズ更新
     */
    updateSize(width, height) {
        this.width = width;
        this.height = height;
        this.offsetX = width / 2;
        this.offsetY = height / 2;
    }

    /**
     * 開口部描画（窓・ドア）
     */
    drawOpenings(openings, selectedItem) {
        if (!openings) return;

        openings.forEach(opening => {
            const pos = this.worldToScreen(opening.position[0], opening.position[1]);
            const widthPx = opening.width * this.scale;
            const isSelected = selectedItem?.type === 'opening' && selectedItem?.id === opening.id;
            // シンプル化: type フィールドを直接使用 (後方互換性のためcategoryもチェック)
            const isWindow = opening.type === 'window' || opening.category === 'window';

            // 色設定
            const color = isWindow ? '#2196F3' : '#8D6E63';
            const bgColor = isWindow ? '#E3F2FD' : '#EFEBE9';

            // 回転角度（0, 90, 180, 270の4パターン）
            const rotation = opening.rotation || 0;
            const halfW = widthPx / 2;
            const depth = 8;

            this.ctx.save();
            this.ctx.translate(pos.x, pos.y);

            // rotation値に応じて回転（度をラジアンに変換）
            this.ctx.rotate((rotation * Math.PI) / 180);

            // 背景
            this.ctx.fillStyle = bgColor;
            this.ctx.fillRect(-halfW, -depth, widthPx, depth * 2);

            // 枠線
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = isSelected ? 3 : 2;
            this.ctx.strokeRect(-halfW, -depth, widthPx, depth * 2);

            if (isWindow) {
                // 窓：中央に線
                this.ctx.beginPath();
                this.ctx.moveTo(-halfW, 0);
                this.ctx.lineTo(halfW, 0);
                this.ctx.stroke();
            } else {
                // ドア：開閉弧（開く方向を示す）
                this.ctx.beginPath();
                this.ctx.moveTo(-halfW + 2, -depth + 2);
                this.ctx.lineTo(-halfW + 2, depth * 2);
                this.ctx.arc(-halfW + 2, -depth + 2, widthPx * 0.8, Math.PI / 2, 0, true);
                this.ctx.stroke();

                // ヒンジ位置を示す小さな丸
                this.ctx.beginPath();
                this.ctx.arc(-halfW + 2, 0, 3, 0, Math.PI * 2);
                this.ctx.fillStyle = color;
                this.ctx.fill();
            }

            // 選択時のハイライト
            if (isSelected) {
                this.ctx.strokeStyle = '#1d4ed8';
                this.ctx.setLineDash([4, 4]);
                this.ctx.strokeRect(-halfW - 4, -depth - 4, widthPx + 8, depth * 2 + 8);
                this.ctx.setLineDash([]);

                // 回転角度表示
                this.ctx.fillStyle = '#1d4ed8';
                this.ctx.font = 'bold 10px sans-serif';
                this.ctx.textAlign = 'center';
                this.ctx.fillText(`${rotation}°`, 0, depth + 18);
            }

            this.ctx.restore();

            // ラベル（選択時以外）
            if (!isSelected) {
                this.ctx.fillStyle = '#333';
                this.ctx.font = '10px sans-serif';
                this.ctx.textAlign = 'center';
                const label = isWindow ? '窓' : '🚪';
                this.ctx.fillText(label, pos.x, pos.y + 20);
            }
        });
    }
}
