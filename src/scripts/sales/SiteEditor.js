/**
 * 敷地エディタ - 敷地ポリゴンの入力・編集
 */
export class SiteEditor {
    constructor(app) {
        this.app = app;
        this.tempPoints = [];
        this.isDrawing = false;
    }

    /**
     * リセット
     */
    reset() {
        this.tempPoints = [];
        this.isDrawing = false;
    }

    /**
     * マウスダウン
     */
    onMouseDown(screenPos) {
        // 敷地が確定済みなら何もしない
        if (this.app.schema.site.polygon.length >= 4 && !this.isDrawing) {
            return;
        }

        const worldPos = this.app.renderer.screenToWorld(screenPos.x, screenPos.y);

        this.app.saveState();
        this.isDrawing = true;

        // 頂点追加
        this.app.schema.site.polygon.push([worldPos.x, worldPos.y]);

        // 4点配置したら自動的に終了
        if (this.app.schema.site.polygon.length === 4) {
            this.finishSite();
        }
    }

    /**
     * マウス移動
     */
    onMouseMove(screenPos) {
        if (!this.isDrawing) {
            this.tempPoints = [];
            return;
        }

        const worldPos = this.app.renderer.screenToWorld(screenPos.x, screenPos.y);
        this.tempPoints = [{ x: worldPos.x, y: worldPos.y }];
    }

    /**
     * 敷地確定
     */
    finishSite() {
        if (this.app.schema.site.polygon.length >= 3) {
            this.isDrawing = false;
            this.tempPoints = [];
            console.log('Site finished:', this.app.schema.site.polygon);
        }
    }

    /**
     * 数値入力（間口・奥行）による長方形敷地の作成
     */
    setRectSite(width, depth) {
        this.app.saveState();

        // 原点を中心（または左下）とした長方形を作成
        // ここでは(0,0)を左下として作成
        this.app.schema.site.polygon = [
            [0, 0],
            [width, 0],
            [width, depth],
            [0, depth]
        ];

        this.isDrawing = false;
        this.tempPoints = [];
        this.app.render();
    }
}
