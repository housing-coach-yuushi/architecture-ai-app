/**
 * 開口部配置 - 窓・ドアのドラッグ＆ドロップ、移動、壁スナップ
 */
export class OpeningPlacer {
    constructor(app) {
        this.app = app;
        this.dragging = null;
        this.dragOffset = { x: 0, y: 0 };
        this.snapDistance = 0.3; // スナップ距離 (m)
    }

    /**
     * マウスダウン - 開口部選択
     */
    onMouseDown(screenPos) {
        const worldPos = this.app.renderer.screenToWorld(screenPos.x, screenPos.y);

        // クリック位置の開口部を探す
        const opening = this.findOpeningAt(worldPos);

        if (opening) {
            this.app.selectedItem = { type: 'opening', id: opening.id };
            this.dragging = opening;
            this.dragOffset = {
                x: opening.position[0] - worldPos.x,
                y: opening.position[1] - worldPos.y,
            };
            this.app.saveState();
        } else {
            // 開口部以外をクリックした場合は選択解除
            if (this.app.selectedItem?.type === 'opening') {
                this.app.selectedItem = null;
            }
        }
    }

    /**
     * マウス移動 - ドラッグ
     */
    onMouseMove(screenPos) {
        if (!this.dragging) return;

        const worldPos = this.app.renderer.screenToWorld(screenPos.x, screenPos.y);

        // 新しい位置を計算
        let newX = worldPos.x + this.dragOffset.x;
        let newY = worldPos.y + this.dragOffset.y;

        // 壁にスナップ
        const snapped = this.snapToWall(newX, newY, this.dragging);

        this.dragging.position = [snapped.x, snapped.y];

        // 壁にスナップした場合、壁の角度に合わせて回転を設定
        if (snapped.wall && snapped.rotation !== undefined) {
            this.dragging.rotation = snapped.rotation;
        }

        this.dragging._snappedWall = snapped.wall;
    }

    /**
     * マウスアップ - ドロップ
     */
    onMouseUp(screenPos) {
        if (this.dragging) {
            this.dragging._snappedWall = null;
            this.app.schema.metadata.updated_at = new Date().toISOString();
        }
        this.dragging = null;
    }

    /**
     * 指定座標の開口部を探す
     */
    findOpeningAt(worldPos) {
        const openings = this.app.schema.openings || [];

        for (let i = openings.length - 1; i >= 0; i--) {
            const opening = openings[i];
            const [ox, oy] = opening.position;
            const halfWidth = opening.width / 2;
            const hitRadius = 0.3; // クリック判定範囲

            // 回転を考慮したヒット判定（簡略化のため円形判定）
            const distance = Math.sqrt((worldPos.x - ox) ** 2 + (worldPos.y - oy) ** 2);
            if (distance <= halfWidth + hitRadius) {
                return opening;
            }
        }
        return null;
    }

    /**
     * 壁にスナップ
     */
    snapToWall(x, y, opening) {
        const rooms = this.app.schema.rooms || [];
        let bestSnap = { x, y, direction: opening.direction, wall: null, distance: Infinity };

        for (const room of rooms) {
            if (!room.polygon || room.polygon.length < 3) continue;

            const walls = this.getWallsFromPolygon(room.polygon);

            for (const wall of walls) {
                const snap = this.snapToWallSegment(x, y, wall, opening.width);

                if (snap && snap.distance < bestSnap.distance && snap.distance < this.snapDistance) {
                    bestSnap = snap;
                }
            }
        }

        // 敷地の辺にもスナップ
        const sitePolygon = this.app.schema.site?.polygon;
        if (sitePolygon && sitePolygon.length >= 3) {
            const siteWalls = this.getWallsFromPolygon(sitePolygon);
            for (const wall of siteWalls) {
                const snap = this.snapToWallSegment(x, y, wall, opening.width);
                if (snap && snap.distance < bestSnap.distance && snap.distance < this.snapDistance) {
                    bestSnap = snap;
                }
            }
        }

        return bestSnap;
    }

    /**
     * ポリゴンから壁セグメントを取得
     */
    getWallsFromPolygon(polygon) {
        const walls = [];
        const n = polygon.length;

        for (let i = 0; i < n; i++) {
            const start = polygon[i];
            const end = polygon[(i + 1) % n];

            walls.push({
                start: { x: start[0], y: start[1] },
                end: { x: end[0], y: end[1] },
            });
        }

        return walls;
    }

    /**
     * 壁セグメントへのスナップを計算
     */
    snapToWallSegment(x, y, wall, openingWidth) {
        const { start, end } = wall;

        // 壁の方向ベクトル
        const dx = end.x - start.x;
        const dy = end.y - start.y;
        const wallLength = Math.sqrt(dx * dx + dy * dy);

        if (wallLength < openingWidth) return null; // 壁が短すぎる

        // 正規化
        const nx = dx / wallLength;
        const ny = dy / wallLength;

        // 点から壁への投影
        const px = x - start.x;
        const py = y - start.y;
        let t = (px * nx + py * ny);

        // 開口部が壁からはみ出さないように制限
        const halfWidth = openingWidth / 2;
        t = Math.max(halfWidth, Math.min(wallLength - halfWidth, t));

        // 壁上の最近点
        const closestX = start.x + t * nx;
        const closestY = start.y + t * ny;

        // 距離を計算
        const distance = Math.sqrt((x - closestX) ** 2 + (y - closestY) ** 2);

        // 壁の角度を計算（ラジアン→度数、45度刻みに丸める）
        const angleRad = Math.atan2(dy, dx);
        const angleDeg = (angleRad * 180 / Math.PI + 360) % 360;
        // 45度刻みに丸める
        const rotation = Math.round(angleDeg / 45) * 45 % 360;

        return {
            x: closestX,
            y: closestY,
            rotation: rotation,
            wall: wall,
            distance: distance,
        };
    }

    /**
     * ダブルクリック - 開口部の向きを8方向まるの回転（45度ずつ）
     */
    onDoubleClick(screenPos) {
        const worldPos = this.app.renderer.screenToWorld(screenPos.x, screenPos.y);
        const opening = this.findOpeningAt(worldPos);

        if (opening) {
            this.app.saveState();
            // 45度ずつ回転（8方向: 0, 45, 90, 135, 180, 225, 270, 315）
            const currentRotation = opening.rotation || 0;
            opening.rotation = (currentRotation + 45) % 360;
            return true;
        }
        return false;
    }
}
