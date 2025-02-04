import { ItemTypes } from './Constants.js'
import { useDrag } from 'react-dnd'
import Image from 'react-bootstrap/Image'
import 'bootstrap/dist/css/bootstrap.min.css';

function DraggableImage({ idx, src }) {
    const [{ isDragging }, drag] = useDrag({
        item: { type: ItemTypes.IMAGE, idx: idx },
        collect: (monitor) => ({
            isDragging: !!monitor.isDragging()
        })
    });
    return <Image width="250" max-width="100%" max-height="100%" ref={drag} className="m-2" src={src} style={{ opacity: isDragging ? 0.5 : 1 }} />
}

export default DraggableImage;
