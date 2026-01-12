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
        const worldPos = this.app.renderer.screenToWorld(screenPos.x, screenPos.y);

        // 敷地が確定済みなら何もしない
        if (this.app.schema.site.polygon.length >= 3 && !this.isDrawing) {
            return;
        }

        this.app.saveState();
        this.isDrawing = true;

        // 頂点追加
        this.app.schema.site.polygon.push([worldPos.x, worldPos.y]);
    }

    /**
     * マウス移動
     */
    onMouseMove(screenPos) {
        if (!this.isDrawing && this.app.schema.site.polygon.length === 0) {
            return;
        }

        const worldPos = this.app.renderer.screenToWorld(screenPos.x, screenPos.y);

        // 仮の点を更新
        if (this.isDrawing || this.app.schema.site.polygon.length > 0) {
            this.tempPoints = [{ x: worldPos.x, y: worldPos.y }];
        }
    }

    /**
     * 敷地確定（ダブルクリック時）
     */
    finishSite() {
        if (this.app.schema.site.polygon.length >= 3) {
            this.isDrawing = false;
            this.tempPoints = [];
            console.log('Site finished:', this.app.schema.site.polygon);
        }
    }
}
