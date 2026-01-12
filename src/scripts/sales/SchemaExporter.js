/**
 * スキーマエクスポーター - LayoutSchema JSONを生成
 */
export class SchemaExporter {
    /**
     * スキーマをエクスポート用に整形
     */
    export(schema) {
        // 更新日時を設定
        const exportSchema = {
            ...schema,
            metadata: {
                ...schema.metadata,
                updated_at: new Date().toISOString(),
            },
        };

        // 内部用プロパティを除去
        exportSchema.rooms = schema.rooms.map(room => {
            const { bounds, ...rest } = room;
            return rest;
        });

        return exportSchema;
    }

    /**
     * BlueprintJS形式に変換
     */
    toBlueprintJS(schema) {
        // BlueprintJSのフォーマットに変換
        const corners = {};
        const walls = [];

        // 敷地ポリゴンを壁に変換
        if (schema.site.polygon.length >= 3) {
            schema.site.polygon.forEach((point, index) => {
                const id = this.generateUUID();
                corners[id] = {
                    x: point[0],
                    y: point[1],
                    elevation: 2.5,
                };
            });
        }

        // TODO: 部屋を壁に変換
        // TODO: 設備をアイテムに変換

        return {
            floorplan: {
                version: "2.0.1a",
                corners,
                walls,
                rooms: {},
                units: "m",
            },
            items: [],
        };
    }

    /**
     * UUID生成
     */
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
}
