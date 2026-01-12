/**
 * 部屋配置 - 部屋ブロックのドラッグ＆ドロップ、リサイズ操作
 */
export class RoomPlacer {
    constructor(app) {
        this.app = app;
        this.dragging = null;
        this.resizing = null;
        this.resizeCorner = null; // 'nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w'
        this.dragOffset = { x: 0, y: 0 };
        this.resizeHandleSize = 0.3; // リサイズハンドルのサイズ (m)
        this.minRoomSize = 0.5; // 最小部屋サイズ (m) - 3尺(約0.91m)対応
        this.snapDistance = 0.5; // スナップ距離 (m)
    }

    /**
     * マウスダウン - 部屋選択/リサイズ開始
     */
    onMouseDown(screenPos) {
        const worldPos = this.app.renderer.screenToWorld(screenPos.x, screenPos.y);

        // まず選択中の部屋のリサイズハンドルをチェック
        if (this.app.selectedItem && this.app.selectedItem.type === 'room') {
            const selectedRoom = this.app.schema.rooms.find(r => r.id === this.app.selectedItem.id);
            if (selectedRoom) {
                const corner = this.findResizeHandle(worldPos, selectedRoom);
                if (corner) {
                    this.resizing = selectedRoom;
                    this.resizeCorner = corner;
                    this.app.saveState();
                    return;
                }
            }
        }

        // クリック位置の部屋を探す
        const room = this.findRoomAt(worldPos);

        if (room) {
            this.app.selectedItem = { type: 'room', id: room.id };
            this.dragging = room;
            this.dragOffset = {
                x: room.bounds.x + room.bounds.width / 2 - worldPos.x,
                y: room.bounds.y + room.bounds.height / 2 - worldPos.y,
            };
            this.app.saveState();
        } else {
            this.app.selectedItem = null;
        }
    }

    /**
     * マウス移動 - ドラッグ/リサイズ
     */
    onMouseMove(screenPos) {
        const worldPos = this.app.renderer.screenToWorld(screenPos.x, screenPos.y);

        // リサイズ中
        if (this.resizing) {
            this.handleResize(worldPos);
            return;
        }

        // ドラッグ中
        if (this.dragging) {
            let newCenterX = worldPos.x + this.dragOffset.x;
            let newCenterY = worldPos.y + this.dragOffset.y;

            // 仮の新boundsを計算
            const newBounds = {
                x: newCenterX - this.dragging.bounds.width / 2,
                y: newCenterY - this.dragging.bounds.height / 2,
                width: this.dragging.bounds.width,
                height: this.dragging.bounds.height,
            };

            // スナップ処理
            const snapped = this.snapToOtherRooms(newBounds, this.dragging.id);
            newCenterX = snapped.x + snapped.width / 2;
            newCenterY = snapped.y + snapped.height / 2;

            // 移動量を計算
            const oldCenterX = this.dragging.bounds.x + this.dragging.bounds.width / 2;
            const oldCenterY = this.dragging.bounds.y + this.dragging.bounds.height / 2;
            const deltaX = newCenterX - oldCenterX;
            const deltaY = newCenterY - oldCenterY;

            // bounds を更新
            this.dragging.bounds.x = snapped.x;
            this.dragging.bounds.y = snapped.y;
            this.dragging.position_hint = [newCenterX, newCenterY];

            // polygon がある場合、全頂点を移動
            if (this.dragging.polygon) {
                this.dragging.polygon = this.dragging.polygon.map(([x, y]) => [
                    x + deltaX,
                    y + deltaY
                ]);
            }

            // 重なりチェック
            this.checkOverlap(this.dragging);
            return;
        }

        // カーソル変更（リサイズハンドル上ならサイズ変更カーソル）
        if (this.app.selectedItem && this.app.selectedItem.type === 'room') {
            const selectedRoom = this.app.schema.rooms.find(r => r.id === this.app.selectedItem.id);
            if (selectedRoom) {
                const corner = this.findResizeHandle(worldPos, selectedRoom);
                if (corner) {
                    this.app.canvas.style.cursor = this.getResizeCursor(corner);
                    return;
                }
            }
        }
        this.app.canvas.style.cursor = 'default';
    }

    /**
     * マウスアップ - ドロップ/リサイズ終了
     */
    onMouseUp(screenPos) {
        if (this.dragging || this.resizing) {
            this.app.schema.metadata.updated_at = new Date().toISOString();
            this.updateRoomArea(this.dragging || this.resizing);
        }
        this.dragging = null;
        this.resizing = null;
        this.resizeCorner = null;
    }

    /**
     * リサイズハンドルを探す（4角 + 4辺）
     */
    findResizeHandle(worldPos, room) {
        const b = room.bounds;
        const hs = this.resizeHandleSize;
        const centerX = b.x + b.width / 2;
        const centerY = b.y + b.height / 2;

        // 4角のハンドル
        const corners = {
            'nw': { x: b.x, y: b.y + b.height },
            'ne': { x: b.x + b.width, y: b.y + b.height },
            'sw': { x: b.x, y: b.y },
            'se': { x: b.x + b.width, y: b.y },
        };

        for (const [corner, pos] of Object.entries(corners)) {
            if (Math.abs(worldPos.x - pos.x) <= hs && Math.abs(worldPos.y - pos.y) <= hs) {
                return corner;
            }
        }

        // 4辺のハンドル（幅・高さ単独調整用）
        const edges = {
            'n': { x: centerX, y: b.y + b.height },  // 上辺
            's': { x: centerX, y: b.y },              // 下辺
            'e': { x: b.x + b.width, y: centerY },   // 右辺
            'w': { x: b.x, y: centerY },              // 左辺
        };

        for (const [edge, pos] of Object.entries(edges)) {
            if (Math.abs(worldPos.x - pos.x) <= hs && Math.abs(worldPos.y - pos.y) <= hs) {
                return edge;
            }
        }

        return null;
    }

    /**
     * リサイズ処理
     */
    handleResize(worldPos) {
        const b = this.resizing.bounds;
        const minSize = this.minRoomSize;

        switch (this.resizeCorner) {
            // 4角のリサイズ
            case 'se':
                b.width = Math.max(minSize, worldPos.x - b.x);
                b.height = Math.max(minSize, worldPos.y - b.y);
                break;
            case 'sw':
                const newWidthSW = b.x + b.width - worldPos.x;
                if (newWidthSW >= minSize) {
                    b.x = worldPos.x;
                    b.width = newWidthSW;
                }
                b.height = Math.max(minSize, worldPos.y - b.y);
                break;
            case 'ne':
                b.width = Math.max(minSize, worldPos.x - b.x);
                const newHeightNE = b.y + b.height - worldPos.y;
                if (newHeightNE >= minSize) {
                    b.y = worldPos.y;
                    b.height = newHeightNE;
                }
                break;
            case 'nw':
                const newWidthNW = b.x + b.width - worldPos.x;
                const newHeightNW = b.y + b.height - worldPos.y;
                if (newWidthNW >= minSize) {
                    b.x = worldPos.x;
                    b.width = newWidthNW;
                }
                if (newHeightNW >= minSize) {
                    b.y = worldPos.y;
                    b.height = newHeightNW;
                }
                break;

            // 4辺のリサイズ（高さ or 幅のみ）
            // 注: 画面座標ではY軸が反転しているため、nが下、sが上
            case 'n':  // 画面上の上辺 = ワールド座標のY+方向
                b.height = Math.max(minSize, worldPos.y - b.y);
                break;
            case 's':  // 画面上の下辺 = ワールド座標のY-方向
                const newHeightS = b.y + b.height - worldPos.y;
                if (newHeightS >= minSize) {
                    b.y = worldPos.y;
                    b.height = newHeightS;
                }
                break;
            case 'e':  // 右辺（幅調整）
                b.width = Math.max(minSize, worldPos.x - b.x);
                break;
            case 'w':  // 左辺（幅調整）
                const newWidthW = b.x + b.width - worldPos.x;
                if (newWidthW >= minSize) {
                    b.x = worldPos.x;
                    b.width = newWidthW;
                }
                break;
        }

        // 位置ヒント更新
        this.resizing.position_hint = [
            b.x + b.width / 2,
            b.y + b.height / 2
        ];

        // polygon がある場合、boundsに合わせて再生成
        if (this.resizing.polygon) {
            this.regeneratePolygonFromBounds(this.resizing);
        }

        // 重なりチェック
        this.checkOverlap(this.resizing);
    }

    /**
     * boundsからpolygonを再生成
     */
    regeneratePolygonFromBounds(room) {
        const b = room.bounds;
        const shape = room.preset_shape || 'rectangle';
        const centerX = b.x + b.width / 2;
        const centerY = b.y + b.height / 2;

        switch (shape) {
            case 'L':
                // L字型（右下が欠けた形）
                const cutW = b.width * 0.4;
                const cutH = b.height * 0.4;
                room.polygon = [
                    [b.x, b.y],
                    [b.x + b.width, b.y],
                    [b.x + b.width, b.y + b.height - cutH],
                    [b.x + b.width - cutW, b.y + b.height - cutH],
                    [b.x + b.width - cutW, b.y + b.height],
                    [b.x, b.y + b.height],
                ];
                break;

            case 'U':
                // コの字型
                const uCutW = b.width * 0.4;
                const uCutH = b.height * 0.4;
                room.polygon = [
                    [b.x, b.y],
                    [centerX - uCutW / 2, b.y],
                    [centerX - uCutW / 2, b.y + uCutH],
                    [centerX + uCutW / 2, b.y + uCutH],
                    [centerX + uCutW / 2, b.y],
                    [b.x + b.width, b.y],
                    [b.x + b.width, b.y + b.height],
                    [b.x, b.y + b.height],
                ];
                break;

            case 'custom':
                // カスタム形状はスケーリングで対応（簡易版：boundsにフィットさせる）
                // 元のpolygonのboundsを計算
                let minX = Infinity, maxX = -Infinity;
                let minY = Infinity, maxY = -Infinity;
                room.polygon.forEach(([x, y]) => {
                    minX = Math.min(minX, x);
                    maxX = Math.max(maxX, x);
                    minY = Math.min(minY, y);
                    maxY = Math.max(maxY, y);
                });
                const oldW = maxX - minX || 1;
                const oldH = maxY - minY || 1;
                const scaleX = b.width / oldW;
                const scaleY = b.height / oldH;
                const oldCenterX = (minX + maxX) / 2;
                const oldCenterY = (minY + maxY) / 2;

                room.polygon = room.polygon.map(([x, y]) => [
                    centerX + (x - oldCenterX) * scaleX,
                    centerY + (y - oldCenterY) * scaleY
                ]);
                break;

            case 'rectangle':
            default:
                // 矩形
                room.polygon = [
                    [b.x, b.y],
                    [b.x + b.width, b.y],
                    [b.x + b.width, b.y + b.height],
                    [b.x, b.y + b.height],
                ];
                break;
        }
    }

    /**
     * リサイズカーソルを取得
     */
    getResizeCursor(corner) {
        const cursors = {
            // 4角
            'nw': 'nwse-resize',
            'se': 'nwse-resize',
            'ne': 'nesw-resize',
            'sw': 'nesw-resize',
            // 4辺
            'n': 'ns-resize',
            's': 'ns-resize',
            'e': 'ew-resize',
            'w': 'ew-resize',
        };
        return cursors[corner] || 'default';
    }

    /**
     * 部屋の面積を更新
     */
    updateRoomArea(room) {
        if (room && room.bounds) {
            room.target_area = Math.round(room.bounds.width * room.bounds.height * 10) / 10;
            this.app.updatePlacedList();
            this.app.updateTotalArea();
        }
    }

    /**
     * 重なりをチェックして警告
     */
    checkOverlap(movingRoom) {
        if (!movingRoom || !movingRoom.bounds) return false;

        const b1 = movingRoom.bounds;
        let hasOverlap = false;

        for (const room of this.app.schema.rooms) {
            if (room.id === movingRoom.id || !room.bounds) continue;

            const b2 = room.bounds;

            // 矩形の重なり判定
            if (b1.x < b2.x + b2.width &&
                b1.x + b1.width > b2.x &&
                b1.y < b2.y + b2.height &&
                b1.y + b1.height > b2.y) {
                hasOverlap = true;
                room._overlapping = true;
            } else {
                room._overlapping = false;
            }
        }

        movingRoom._overlapping = hasOverlap;
        return hasOverlap;
    }

    /**
     * 指定座標の部屋を探す
     */
    findRoomAt(worldPos) {
        // 逆順（上のレイヤーから）
        for (let i = this.app.schema.rooms.length - 1; i >= 0; i--) {
            const room = this.app.schema.rooms[i];
            if (!room.bounds) continue;

            const b = room.bounds;
            if (worldPos.x >= b.x && worldPos.x <= b.x + b.width &&
                worldPos.y >= b.y && worldPos.y <= b.y + b.height) {
                return room;
            }
        }
        return null;
    }

    /**
     * 他の部屋の辺にスナップ
     */
    snapToOtherRooms(bounds, excludeId) {
        const snap = this.snapDistance;
        let snappedX = bounds.x;
        let snappedY = bounds.y;

        // 現在の部屋の4辺
        const myLeft = bounds.x;
        const myRight = bounds.x + bounds.width;
        const myTop = bounds.y + bounds.height;
        const myBottom = bounds.y;

        // 他の部屋と比較
        for (const other of this.app.schema.rooms) {
            if (other.id === excludeId || !other.bounds) continue;

            const ob = other.bounds;
            const otherLeft = ob.x;
            const otherRight = ob.x + ob.width;
            const otherTop = ob.y + ob.height;
            const otherBottom = ob.y;

            // Y方向が重なっているか確認（上下スナップ用）
            const yOverlap = !(myTop < otherBottom || myBottom > otherTop);
            // X方向が重なっているか確認（左右スナップ用）
            const xOverlap = !(myRight < otherLeft || myLeft > otherRight);

            // 左辺 → 他の右辺にスナップ
            if (Math.abs(myLeft - otherRight) < snap && yOverlap) {
                snappedX = otherRight;
            }
            // 右辺 → 他の左辺にスナップ
            if (Math.abs(myRight - otherLeft) < snap && yOverlap) {
                snappedX = otherLeft - bounds.width;
            }
            // 下辺 → 他の上辺にスナップ
            if (Math.abs(myBottom - otherTop) < snap && xOverlap) {
                snappedY = otherTop;
            }
            // 上辺 → 他の下辺にスナップ
            if (Math.abs(myTop - otherBottom) < snap && xOverlap) {
                snappedY = otherBottom - bounds.height;
            }

            // 辺揃え（同じ位置の辺を揃える）
            if (Math.abs(myLeft - otherLeft) < snap) {
                snappedX = otherLeft;
            }
            if (Math.abs(myRight - otherRight) < snap) {
                snappedX = otherRight - bounds.width;
            }
            if (Math.abs(myTop - otherTop) < snap) {
                snappedY = otherTop - bounds.height;
            }
            if (Math.abs(myBottom - otherBottom) < snap) {
                snappedY = otherBottom;
            }
        }

        return {
            x: snappedX,
            y: snappedY,
            width: bounds.width,
            height: bounds.height,
        };
    }
}
