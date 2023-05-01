import React from 'react';

function Header() {
    return (
        <>
            <div className="text-center">
                <img
                    src={require('./iscte_logo_no_back.png')}
                    width="300"
                    alt="ISCTE"
                    className="img-thumbnail"
                    style={{marginTop: "20px"}}
                />
                <br/>
                <br/>
                <h5>
                    <i>Desenvolvimento para a Internet e Aplicações Móveis (LEI e LIGE)</i>
                </h5>
                <br/>
                <hr/>
                <br/>
                <h2>Exemplo de integração de Django com React</h2>
                <br/>
            </div>
        </>
    );
}

export default Header;