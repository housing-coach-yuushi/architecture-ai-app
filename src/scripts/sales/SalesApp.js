/**
 * セットプラン 営業モード - メインアプリケーション
 */

import { CanvasRenderer } from './CanvasRenderer.js';
import { SiteEditor } from './SiteEditor.js';
import { RoomPlacer } from './RoomPlacer.js';
import { OpeningPlacer } from './OpeningPlacer.js';
import { SchemaExporter } from './SchemaExporter.js';

// 部屋タイプ定義
const ROOM_TYPES = {
    LDK: { label: 'LDK', color: '#4CAF50', defaultArea: 28 },
    bedroom: { label: '寝室', color: '#2196F3', defaultArea: 12 },
    children_room: { label: '子供部屋', color: '#03A9F4', defaultArea: 8 },
    japanese_room: { label: '和室', color: '#8BC34A', defaultArea: 10 },
    bathroom: { label: '浴室', color: '#00BCD4', defaultArea: 4 },
    washroom: { label: '洗面', color: '#00ACC1', defaultArea: 3 },
    toilet: { label: 'トイレ', color: '#26C6DA', defaultArea: 2 },
    entrance: { label: '玄関', color: '#FF9800', defaultArea: 4 },
    hallway: { label: '廊下', color: '#FFC107', defaultArea: 6 },
    closet: { label: '収納', color: '#795548', defaultArea: 3 },
};

// 設備ユニット定義
const UNIT_TYPES = {
    bath: { label: '浴室ユニット', sizes: ['1216', '1616', '1620', '1624'] },
    toilet: { label: 'トイレ', sizes: ['standard', 'wide'] },
    washstand: { label: '洗面台', sizes: ['600', '750', '900', '1200'] },
    kitchen: { label: 'キッチン', sizes: ['I_2400', 'I_2500', 'I_2700', 'L_2400', 'L_2500', 'island'] },
    stair: { label: '階段', sizes: ['straight', 'U_left', 'U_right'] },
    // 家具
    dining_table: { label: 'ダイニングテーブル', sizes: ['4人', '6人', '8人'] },
    sofa: { label: 'ソファ', sizes: ['2P', '3P', 'L字'] },
    tv: { label: 'テレビ', sizes: ['55型', '65型', '75型'] },
};

/**
 * メインアプリケーションクラス
 */
class SalesApp {
    constructor() {
        // 状態
        this.currentMode = 'site'; // 'site' | 'room' | 'unit'
        this.selectedShape = 'rectangle'; // 'rectangle' | 'L' | 'U' | 'custom'
        this.customDrawingState = null; // 自由多角形描画中の状態
        this.customTempPoints = []; // 仮の頂点
        this.schema = this.createEmptySchema();
        this.selectedItem = null;
        this.undoStack = [];
        this.isPanning = false;
        this.lastMousePos = { x: 0, y: 0 };

        // コンポーネント初期化
        this.initCanvas();
        this.initComponents();
        this.bindEvents();

        // 初期描画
        this.render();

        console.log('SalesApp initialized');
    }

    /**
     * 空のスキーマを生成
     */
    createEmptySchema() {
        return {
            metadata: {
                version: '1.0.0',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                project_name: '新規プロジェクト',
            },
            site: {
                polygon: [],
                north: [0, 1],
            },
            grid: {
                module: 910,
                visible: true,
            },
            rooms: [],
            units: [],
            openings: [],
            adjacency: [],
        };
    }

    /**
     * キャンバス初期化
     */
    initCanvas() {
        this.canvas = document.getElementById('main-canvas');
        this.ctx = this.canvas.getContext('2d');

        // リサイズ対応
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }

    /**
     * キャンバスサイズ調整
     */
    resizeCanvas() {
        const container = this.canvas.parentElement;
        const dpr = window.devicePixelRatio || 1;

        this.canvas.width = container.clientWidth * dpr;
        this.canvas.height = container.clientHeight * dpr;

        this.ctx.scale(dpr, dpr);

        this.canvasWidth = container.clientWidth;
        this.canvasHeight = container.clientHeight;

        this.render();
    }

    /**
     * コンポーネント初期化
     */
    initComponents() {
        this.renderer = new CanvasRenderer(this.ctx, this.canvasWidth, this.canvasHeight);
        this.siteEditor = new SiteEditor(this);
        this.roomPlacer = new RoomPlacer(this);
        this.openingPlacer = new OpeningPlacer(this);
        this.exporter = new SchemaExporter();
    }

    /**
     * イベントバインド
     */
    bindEvents() {
        // モード切替
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.switchMode(mode);
            });
        });

        // 敷地クリア
        document.getElementById('btn-clear-site').addEventListener('click', () => {
            this.clearSite();
        });

        // 敷地寸法入力
        document.getElementById('btn-apply-site-rect').addEventListener('click', () => {
            const width = parseFloat(document.getElementById('site-width').value);
            const depth = parseFloat(document.getElementById('site-depth').value);
            if (!isNaN(width) && !isNaN(depth) && width > 0 && depth > 0) {
                this.siteEditor.setRectSite(width, depth);
            } else {
                alert('有効な数値を入力してください');
            }
        });

        // グリッド変更
        document.getElementById('grid-module').addEventListener('change', (e) => {
            this.schema.grid.module = parseInt(e.target.value);
            this.render();
        });

        // 北方向
        document.querySelectorAll('.compass-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.compass-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.setNorthDirection(e.target.id);
            });
        });

        // キャンバスイベント
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.onMouseUp(e));
        this.canvas.addEventListener('dblclick', (e) => this.onDoubleClick(e));

        // マウスホイールによるズーム
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const pos = this.getCanvasPosition(e);
            if (e.deltaY < 0) {
                this.renderer.zoomIn(pos.x, pos.y);
            } else {
                this.renderer.zoomOut(pos.x, pos.y);
            }
            this.render();
        }, { passive: false });

        // ドラッグ&ドロップ
        this.canvas.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        });
        this.canvas.addEventListener('drop', (e) => this.onDrop(e));

        // パレットアイテムのドラッグ開始
        document.querySelectorAll('.palette-item').forEach(item => {
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('application/json', JSON.stringify({
                    type: item.dataset.type || null,
                    area: item.dataset.area ? parseFloat(item.dataset.area) : null,
                    unit: item.dataset.unit || null,
                    size: item.dataset.size || null,
                    opening: item.dataset.opening || null,
                    width: item.dataset.width ? parseFloat(item.dataset.width) : null,
                    height: item.dataset.height ? parseFloat(item.dataset.height) : null,
                }));
            });
        });

        // ツールバー
        document.getElementById('btn-zoom-in').addEventListener('click', () => {
            this.renderer.zoomIn();
            this.render();
        });
        document.getElementById('btn-zoom-out').addEventListener('click', () => {
            this.renderer.zoomOut();
            this.render();
        });
        document.getElementById('btn-fit').addEventListener('click', () => this.fitView());
        document.getElementById('btn-undo').addEventListener('click', () => this.undo());
        document.getElementById('btn-delete').addEventListener('click', () => this.deleteSelected());

        // ヘッダー
        document.getElementById('project-name').addEventListener('change', (e) => {
            this.schema.metadata.project_name = e.target.value;
        });
        document.getElementById('btn-save').addEventListener('click', () => this.save());
        document.getElementById('btn-export').addEventListener('click', () => this.showExportModal());

        // モーダル
        document.getElementById('btn-close-modal').addEventListener('click', () => this.hideExportModal());
        document.getElementById('btn-copy-json').addEventListener('click', () => this.copyJson());
        document.getElementById('btn-download-json').addEventListener('click', () => this.downloadJson());

        // 形状選択ボタン
        document.querySelectorAll('.shape-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.shape-btn').forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
                this.selectedShape = e.currentTarget.dataset.shape;

                // カスタムモードのヒント表示
                const hint = document.getElementById('custom-hint');
                if (hint) {
                    hint.style.display = this.selectedShape === 'custom' ? 'block' : 'none';
                }

                // カスタム描画状態リセット
                this.customDrawingState = null;
                this.customTempPoints = [];
            });
        });
    }

    /**
     * モード切替
     */
    switchMode(mode) {
        this.currentMode = mode;

        // ボタン状態更新
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        // パネル表示切替
        document.getElementById('panel-site').style.display = mode === 'site' ? 'block' : 'none';
        document.getElementById('panel-room').style.display = mode === 'room' ? 'block' : 'none';
        document.getElementById('panel-opening').style.display = mode === 'opening' ? 'block' : 'none';
        document.getElementById('panel-unit').style.display = mode === 'unit' ? 'block' : 'none';

        // ステータス更新
        const modeNames = { site: '敷地トレース', room: '部屋配置', opening: '開口部配置', unit: '設備配置' };
        document.getElementById('status-mode').textContent = `モード: ${modeNames[mode]}`;

        // カーソル変更
        this.canvas.style.cursor = mode === 'site' ? 'crosshair' : 'default';

        this.render();
    }

    /**
     * マウスダウン
     */
    onMouseDown(e) {
        const pos = this.getCanvasPosition(e);
        this.lastMousePos = pos;

        // 中ボタン(button:1) または Altキー+左ボタン でパン開始
        if (e.button === 1 || (e.button === 0 && e.altKey)) {
            this.isPanning = true;
            this.canvas.style.cursor = 'grabbing';
            return;
        }

        const worldPos = this.renderer.screenToWorld(pos.x, pos.y);

        if (this.currentMode === 'site') {
            this.siteEditor.onMouseDown(pos);
        } else if (this.currentMode === 'room') {
            // カスタム多角形モード
            if (this.selectedShape === 'custom' && this.customDrawingState) {
                // 頂点追加
                this.customTempPoints.push([worldPos.x, worldPos.y]);
            } else {
                this.roomPlacer.onMouseDown(pos);
            }
        } else if (this.currentMode === 'opening') {
            this.openingPlacer.onMouseDown(pos);
        } else if (this.currentMode === 'unit') {
            // 設備を選択
            const unit = this.findUnitAt(worldPos);
            if (unit) {
                this.selectedItem = { type: 'unit', id: unit.id };
                this.draggingUnit = unit;
                this.unitDragOffset = {
                    x: unit.position_hint[0] - worldPos.x,
                    y: unit.position_hint[1] - worldPos.y,
                };
                this.saveState();
            } else {
                this.selectedItem = null;
                this.draggingUnit = null;
            }
        }

        this.render();
    }

    /**
     * マウス移動
     */
    onMouseMove(e) {
        const pos = this.getCanvasPosition(e);

        if (this.isPanning) {
            const dx = pos.x - this.lastMousePos.x;
            const dy = pos.y - this.lastMousePos.y;
            this.renderer.pan(dx, dy);
            this.lastMousePos = pos;
            this.render();
            return;
        }

        // カーソル位置表示
        const worldPos = this.renderer.screenToWorld(pos.x, pos.y);
        document.getElementById('status-cursor').textContent =
            `カーソル: (${worldPos.x.toFixed(1)}m, ${worldPos.y.toFixed(1)}m)`;

        if (this.currentMode === 'site') {
            this.siteEditor.onMouseMove(pos);
        } else if (this.currentMode === 'room') {
            this.roomPlacer.onMouseMove(pos);
        } else if (this.currentMode === 'opening') {
            this.openingPlacer.onMouseMove(pos);
        } else if (this.currentMode === 'unit' && this.draggingUnit) {
            // 設備を移動
            this.draggingUnit.position_hint = [
                worldPos.x + this.unitDragOffset.x,
                worldPos.y + this.unitDragOffset.y
            ];
        }

        this.render();
        this.lastMousePos = pos;
    }

    /**
     * マウスアップ
     */
    onMouseUp(e) {
        if (this.isPanning) {
            this.isPanning = false;
            this.canvas.style.cursor = this.currentMode === 'site' ? 'crosshair' : 'default';
            return;
        }

        const pos = this.getCanvasPosition(e);

        if (this.currentMode === 'room') {
            this.roomPlacer.onMouseUp(pos);
        } else if (this.currentMode === 'opening') {
            this.openingPlacer.onMouseUp(pos);
        } else if (this.currentMode === 'unit') {
            this.draggingUnit = null;
        }

        this.render();
    }

    /**
     * ダブルクリック
     */
    onDoubleClick(e) {
        const pos = this.getCanvasPosition(e);
        const worldPos = this.renderer.screenToWorld(pos.x, pos.y);

        if (this.currentMode === 'site') {
            this.siteEditor.finishSite();
            this.render();
        } else if (this.currentMode === 'room' && this.selectedShape === 'custom' && this.customDrawingState) {
            // カスタム多角形確定
            this.finishCustomPolygon();
            this.render();
        } else if (this.currentMode === 'opening') {
            // 開口部の向きを回転
            if (this.openingPlacer.onDoubleClick(pos)) {
                this.render();
            }
        } else if (this.currentMode === 'unit') {
            // 設備の向きを45度回転
            const unit = this.findUnitAt(worldPos);
            if (unit) {
                this.saveState();
                unit.rotation = ((unit.rotation || 0) + 45) % 360;
                this.render();
            }
        }
    }

    /**
     * ドロップ
     */
    onDrop(e) {
        e.preventDefault();
        const pos = this.getCanvasPosition(e);
        const worldPos = this.renderer.screenToWorld(pos.x, pos.y);

        try {
            const data = JSON.parse(e.dataTransfer.getData('application/json'));

            if (data.type) {
                // カスタム多角形モードの場合は描画開始
                if (this.selectedShape === 'custom') {
                    this.startCustomPolygonDrawing(data.type, data.area, worldPos);
                } else {
                    // 通常の部屋配置
                    this.addRoom(data.type, data.area, worldPos);
                }
            } else if (data.opening) {
                // 開口部配置（窓・ドア）
                this.addOpening(data.opening, data.width, data.height, worldPos);
            } else if (data.unit) {
                // 設備配置
                this.addUnit(data.unit, data.size, worldPos);
            }
        } catch (err) {
            console.error('Drop error:', err);
        }

        this.render();
    }

    /**
     * カスタム多角形描画開始
     */
    startCustomPolygonDrawing(type, area, startPos) {
        this.customDrawingState = {
            type: type,
            area: area,
        };
        this.customTempPoints = [[startPos.x, startPos.y]];
        this.canvas.style.cursor = 'crosshair';

        document.getElementById('status-mode').textContent =
            'モード: 多角形描画中 (ダブルクリックで確定)';
    }

    /**
     * カスタム多角形確定
     */
    finishCustomPolygon() {
        if (!this.customDrawingState || this.customTempPoints.length < 3) {
            alert('3点以上必要です');
            return;
        }

        const roomType = ROOM_TYPES[this.customDrawingState.type];
        if (!roomType) return;

        const polygon = [...this.customTempPoints];
        const calculatedArea = this.calculatePolygonArea(polygon);
        const bounds = this.calculateBounds(polygon);

        const room = {
            id: `room_${this.customDrawingState.type}_${Date.now()}`,
            type: this.customDrawingState.type,
            target_area: Math.round(calculatedArea * 10) / 10,
            preset_shape: 'custom',
            position_hint: [bounds.x + bounds.width / 2, bounds.y + bounds.height / 2],
            priority: 'prefer',
            polygon: polygon,
            bounds: bounds,
        };

        this.saveState();
        this.schema.rooms.push(room);
        this.updatePlacedList();
        this.updateTotalArea();

        // 状態リセット
        this.customDrawingState = null;
        this.customTempPoints = [];
        this.canvas.style.cursor = 'default';
        document.getElementById('status-mode').textContent = 'モード: 部屋配置';
    }

    /**
     * 部屋追加
     */
    addRoom(type, area, position) {
        const roomType = ROOM_TYPES[type];
        if (!roomType) return;

        // 形状に応じた多角形を生成
        const polygon = this.generateRoomPolygon(area, position, this.selectedShape);

        const room = {
            id: `room_${type}_${Date.now()}`,
            type: type,
            target_area: area,
            preset_shape: this.selectedShape,
            position_hint: [position.x, position.y],
            priority: 'prefer',
            // 多角形座標（ワールド座標、反時計回り）
            polygon: polygon,
            // バウンディングボックス（互換性のため）
            bounds: this.calculateBounds(polygon),
        };

        this.saveState();
        this.schema.rooms.push(room);
        this.updatePlacedList();
        this.updateTotalArea();
    }

    /**
     * 形状に応じた多角形を生成
     */
    generateRoomPolygon(area, center, shape) {
        const side = Math.sqrt(area);
        const halfSide = side / 2;
        const x = center.x;
        const y = center.y;

        switch (shape) {
            case 'L':
                // L字型（右下が欠けた形）
                const lw = side * 1.2;
                const lh = side * 1.2;
                const cutW = lw * 0.4;
                const cutH = lh * 0.4;
                return [
                    [x - lw / 2, y - lh / 2],
                    [x + lw / 2, y - lh / 2],
                    [x + lw / 2, y + lh / 2 - cutH],
                    [x + lw / 2 - cutW, y + lh / 2 - cutH],
                    [x + lw / 2 - cutW, y + lh / 2],
                    [x - lw / 2, y + lh / 2],
                ];

            case 'U':
                // コの字型（上部中央が欠けた形）
                const uw = side * 1.4;
                const uh = side * 1.0;
                const uCutW = uw * 0.4;
                const uCutH = uh * 0.4;
                return [
                    [x - uw / 2, y - uh / 2],
                    [x - uCutW / 2, y - uh / 2],
                    [x - uCutW / 2, y - uh / 2 + uCutH],
                    [x + uCutW / 2, y - uh / 2 + uCutH],
                    [x + uCutW / 2, y - uh / 2],
                    [x + uw / 2, y - uh / 2],
                    [x + uw / 2, y + uh / 2],
                    [x - uw / 2, y + uh / 2],
                ];

            case 'rectangle':
            default:
                // 矩形
                return [
                    [x - halfSide, y - halfSide],
                    [x + halfSide, y - halfSide],
                    [x + halfSide, y + halfSide],
                    [x - halfSide, y + halfSide],
                ];
        }
    }

    /**
     * 多角形からバウンディングボックスを計算
     */
    calculateBounds(polygon) {
        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;

        polygon.forEach(([x, y]) => {
            minX = Math.min(minX, x);
            maxX = Math.max(maxX, x);
            minY = Math.min(minY, y);
            maxY = Math.max(maxY, y);
        });

        return {
            x: minX,
            y: minY,
            width: maxX - minX,
            height: maxY - minY,
        };
    }

    /**
     * 多角形の面積を計算（Shoelace formula）
     */
    calculatePolygonArea(polygon) {
        let area = 0;
        const n = polygon.length;
        for (let i = 0; i < n; i++) {
            const j = (i + 1) % n;
            area += polygon[i][0] * polygon[j][1];
            area -= polygon[j][0] * polygon[i][1];
        }
        return Math.abs(area) / 2;
    }

    /**
     * 設備追加
     */
    addUnit(unitType, size, position) {
        const unit = {
            id: `unit_${unitType}_${Date.now()}`,
            unit_type: unitType,
            size_preset: size,
            position_hint: [position.x, position.y],
            rotation: 0,
        };

        this.saveState();
        this.schema.units.push(unit);
        this.updatePlacedList();
    }

    /**
     * 開口部（窓・ドア）追加
     */
    addOpening(openingType, width, height, position) {
        // 開口部の種類を判別
        const isWindow = openingType.includes('window');
        const isDoor = openingType.includes('door') || openingType === 'entrance';

        const openingWidth = width || (isWindow ? 1.6 : 0.9);

        // 壁にスナップ
        const snapped = this.openingPlacer.snapToWall(position.x, position.y, { width: openingWidth, rotation: 0 });

        // シンプルで明確な構造 (FreeCAD互換)
        const opening = {
            id: `opening_${Date.now()}`,
            type: isWindow ? 'window' : 'door',  // シンプル化: 'window' | 'door'
            position: [snapped.x, snapped.y],
            width: openingWidth,
            height: height || (isWindow ? 1.1 : 2.0),
            rotation: snapped.rotation || 0,
        };

        this.saveState();
        this.schema.openings.push(opening);
        this.updatePlacedList();

        console.log('Opening added:', opening);
    }

    /**
     * 敷地クリア
     */
    clearSite() {
        this.saveState();
        this.schema.site.polygon = [];
        this.siteEditor.reset();
        this.updateTotalArea();
        this.render();
    }

    /**
     * 北方向設定
     */
    setNorthDirection(btnId) {
        const directions = {
            'north-up': [0, 1],
            'north-right': [1, 0],
            'north-down': [0, -1],
            'north-left': [-1, 0],
        };
        this.schema.site.north = directions[btnId] || [0, 1];
        this.render();
    }

    /**
     * キャンバス座標取得
     */
    getCanvasPosition(e) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
        };
    }

    /**
     * 指定座標の設備を探す
     */
    findUnitAt(worldPos) {
        const units = this.schema.units || [];
        const hitRadius = 0.5; // クリック判定範囲 (m)

        for (let i = units.length - 1; i >= 0; i--) {
            const unit = units[i];
            const [ux, uy] = unit.position_hint;
            const distance = Math.sqrt((worldPos.x - ux) ** 2 + (worldPos.y - uy) ** 2);
            if (distance <= hitRadius) {
                return unit;
            }
        }
        return null;
    }

    /**
     * 描画
     */
    render() {
        if (!this.renderer) return;

        this.renderer.clear();
        this.renderer.drawGrid(this.schema.grid);
        this.renderer.drawSite(this.schema.site, this.siteEditor.tempPoints);
        this.renderer.drawRooms(this.schema.rooms, ROOM_TYPES, this.selectedItem);
        this.renderer.drawOpenings(this.schema.openings, this.selectedItem);
        this.renderer.drawUnits(this.schema.units, this.selectedItem);

        // カスタム多角形描画中の仮表示
        if (this.customDrawingState && this.customTempPoints.length > 0) {
            this.drawCustomTempPolygon();
        }
    }

    /**
     * カスタム描画中の仮多角形を描画
     */
    drawCustomTempPolygon() {
        const ctx = this.ctx;
        const points = this.customTempPoints;

        if (points.length === 0) return;

        // 線を描画
        ctx.beginPath();
        const first = this.renderer.worldToScreen(points[0][0], points[0][1]);
        ctx.moveTo(first.x, first.y);

        for (let i = 1; i < points.length; i++) {
            const p = this.renderer.worldToScreen(points[i][0], points[i][1]);
            ctx.lineTo(p.x, p.y);
        }

        // 塗りつぶし（半透明）
        if (points.length >= 3) {
            ctx.closePath();
            const roomType = ROOM_TYPES[this.customDrawingState.type];
            ctx.fillStyle = (roomType?.color || '#888') + '30';
            ctx.fill();
        }

        ctx.strokeStyle = '#1d4ed8';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.stroke();
        ctx.setLineDash([]);

        // 頂点を描画
        points.forEach(([x, y]) => {
            const p = this.renderer.worldToScreen(x, y);
            ctx.beginPath();
            ctx.arc(p.x, p.y, 6, 0, Math.PI * 2);
            ctx.fillStyle = '#1d4ed8';
            ctx.fill();
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 2;
            ctx.stroke();
        });
    }

    /**
     * ビューフィット
     */
    fitView() {
        if (this.schema.site.polygon.length > 0) {
            this.renderer.fitToPolygon(this.schema.site.polygon);
        }
        this.render();
    }

    /**
     * 状態保存（Undo用）
     */
    saveState() {
        this.undoStack.push(JSON.stringify(this.schema));
        if (this.undoStack.length > 50) {
            this.undoStack.shift();
        }
    }

    /**
     * Undo
     */
    undo() {
        if (this.undoStack.length > 0) {
            this.schema = JSON.parse(this.undoStack.pop());
            this.updatePlacedList();
            this.updateTotalArea();
            this.render();
        }
    }

    /**
     * 選択削除
     */
    deleteSelected() {
        if (!this.selectedItem) return;

        this.saveState();

        if (this.selectedItem.type === 'room') {
            this.schema.rooms = this.schema.rooms.filter(r => r.id !== this.selectedItem.id);
        } else if (this.selectedItem.type === 'unit') {
            this.schema.units = this.schema.units.filter(u => u.id !== this.selectedItem.id);
        }

        this.selectedItem = null;
        this.updatePlacedList();
        this.updateTotalArea();
        this.render();
    }

    /**
     * 配置済みリスト更新
     */
    updatePlacedList() {
        const list = document.getElementById('placed-list');

        if (this.schema.rooms.length === 0 && this.schema.units.length === 0) {
            list.innerHTML = '<p class="empty-message">まだ配置されていません</p>';
            return;
        }

        let html = '';

        this.schema.rooms.forEach(room => {
            const roomType = ROOM_TYPES[room.type];
            html += `<div class="placed-item">
                <span><span class="color-dot" style="background:${roomType?.color}"></span> ${roomType?.label || room.type}</span>
                <span>${room.target_area}㎡</span>
            </div>`;
        });

        this.schema.units.forEach(unit => {
            html += `<div class="placed-item">
                <span>${UNIT_TYPES[unit.unit_type]?.label || unit.unit_type}</span>
                <span>${unit.size_preset}</span>
            </div>`;
        });

        list.innerHTML = html;
    }

    /**
     * 総面積更新
     */
    updateTotalArea() {
        // 部屋の合計面積
        const roomsTotal = this.schema.rooms.reduce((sum, room) => sum + (room.target_area || 0), 0);

        // 敷地の面積
        let siteArea = 0;
        if (this.schema.site.polygon && this.schema.site.polygon.length >= 3) {
            siteArea = this.calculatePolygonArea(this.schema.site.polygon);
        }

        const roomsText = `延床面積: ${roomsTotal.toFixed(1)}㎡`;
        const siteText = siteArea > 0 ? ` / 敷地面積: ${siteArea.toFixed(1)}㎡` : '';

        document.getElementById('status-area').textContent = `${roomsText}${siteText}`;
    }

    /**
     * ローカルストレージに保存
     */
    save() {
        this.schema.metadata.updated_at = new Date().toISOString();
        localStorage.setItem('setplan_schema', JSON.stringify(this.schema));
        alert('ブラウザに一時保存しました');
    }

    /**
     * ファイルに名前を付けて保存 (File System Access API)
     */
    async saveToFile() {
        try {
            this.schema.metadata.updated_at = new Date().toISOString();
            const jsonString = JSON.stringify(this.schema, null, 2);

            // 保存ダイアログを表示
            const handle = await window.showSaveFilePicker({
                suggestedName: `${this.schema.metadata.project_name || 'layout'}.json`,
                types: [{
                    description: 'JSON Files',
                    accept: { 'application/json': ['.json'] },
                }],
            });

            // 書き込み
            const writable = await handle.createWritable();
            await writable.write(jsonString);
            await writable.close();

            alert('ファイルを保存しました');
        } catch (err) {
            if (err.name !== 'AbortError') {
                console.error('Save failed:', err);
                alert('保存に失敗しました。ブラウザが対応していない可能性があります。');
            }
        }
    }

    /**
     * ファイルを開く (File System Access API)
     */
    async loadFromFile() {
        try {
            // ファイル選択ダイアログ
            const [handle] = await window.showOpenFilePicker({
                types: [{
                    description: 'JSON Files',
                    accept: { 'application/json': ['.json'] },
                }],
                multiple: false
            });

            // 読み込み
            const file = await handle.getFile();
            const text = await file.text();
            const data = JSON.parse(text);

            // スキーマ検証（簡易）
            if (!data.rooms || !data.metadata) {
                alert('無効なファイル形式です');
                return;
            }

            // データ適用
            this.schema = data;

            // UI更新
            this.render();
            this.updateLists();
            this.updateTotalArea();

            // 敷地面積などが入力フォームにある場合は更新が必要だが、現状はなさそう
            // グリッド幅の反映
            if (this.schema.grid && this.schema.grid.module) {
                const gridInput = document.getElementById('grid-module');
                if (gridInput) gridInput.value = this.schema.grid.module;
            }

            alert('ファイルを読み込みました');

        } catch (err) {
            if (err.name !== 'AbortError') {
                console.error('Load failed:', err);
                alert('読み込みに失敗しました');
            }
        }
    }

    /**
     * AIアプリへ画像を送る (ダウンロード & クリップボード)
     */
    async sendToAIApp() {
        try {
            // 1. キャンバスをBlobに変換
            const blob = await new Promise(resolve => this.canvas.toBlob(resolve, 'image/png'));

            // 2. 画像をダウンロード (ドラッグ&ドロップ用)
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'layout_for_ai.png';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            // 3. クリップボードにも一応コピー (予備)
            try {
                await navigator.clipboard.write([
                    new ClipboardItem({
                        'image/png': blob
                    })
                ]);
            } catch (e) {
                // クリップボード失敗は無視 (ダウンロードがメインなので)
            }

            // 4. アラートで案内
            if (confirm('画像をダウンロードしました (layout_for_ai.png)！\n\n開いたAIアプリの画面に、ダウンロードされたファイルをドラッグ＆ドロップしてください。\n\nAIアプリを開きますか？')) {
                // 5. 外部アプリを開く
                window.open('https://architecture-ai-app-gpx4jqwzktbykcga6evgjv.streamlit.app/', '_blank');
            }

        } catch (err) {
            console.error('Send to AI App failed:', err);
            alert('処理に失敗しました');
        }
    }

    /**
     * エクスポートモーダル表示
     */
    showExportModal() {
        const json = this.exporter.export(this.schema);
        document.getElementById('export-json').value = JSON.stringify(json, null, 2);
        document.getElementById('export-modal').style.display = 'flex';
    }

    /**
     * エクスポートモーダル非表示
     */
    hideExportModal() {
        document.getElementById('export-modal').style.display = 'none';
    }

    /**
     * JSONコピー
     */
    copyJson() {
        const textarea = document.getElementById('export-json');
        textarea.select();
        document.execCommand('copy');
        alert('コピーしました');
    }

    /**
     * JSONダウンロード
     */
    downloadJson() {
        const json = document.getElementById('export-json').value;
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.schema.metadata.project_name || 'layout'}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// アプリ起動
window.addEventListener('DOMContentLoaded', () => {
    window.salesApp = new SalesApp();
});
