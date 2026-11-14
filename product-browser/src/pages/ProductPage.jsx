import {useState, useEffect} from 'react';
import {Link} from 'react-router';
function ProductPage() {
    const[products,setProducts] = useState([]);

    useEffect(() =>{
        async function loadProducts() {
            const res = await fetch('https://dummyjson.com/products');
            const data = await res.json();
        setProducts( data.products );
        }
        loadProducts();

    }, []);
    return (
        <>
        <p> Loaded {products.length} products</p>
        <ul>
            {products.map((product)=>(
                
                <li key ={product.id}>
                    <img src= {product.thumbnail}></img>
                    <h3>{product.title}</h3>
                    <p> Price :${product.price} </p>
                    <p> Rating : {product.rating} </p>
                    <p> category : {product.category} </p>
                    <p>{product.reviews.length} </p>
                    <Link to ={`/product/${product.id}`}>View Details</Link>
                </li>
            ))}
        </ul>
        </>
    );
}

export default  ProductPage;